"""Blind human grading.

Two things make a grade defensible: the grader cannot see which system produced
an answer, and all conditions for one item are graded together so the standard
does not drift between them. Both are enforced here — responses are pooled per
item, shuffled, and relabelled 'System A', 'System B'.

Grades live in grades/grades.jsonl, keyed by response id and appended as you go,
so grading can be stopped and resumed. That file is expensive human labour and
belongs in version control; run outputs are regenerable and do not.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path

from .conditions import CITED_CONDITIONS
from .items import Item, ItemSet


@dataclass
class Grade:
    response_id: str
    item_id: str
    condition: str
    must_include_hits: list[bool]
    must_not_include_hits: list[bool]
    policy_pass: bool | None
    citations_valid: bool | None
    note: str = ""

    @property
    def correctness(self) -> float:
        if not self.must_include_hits:
            return 0.0
        return sum(self.must_include_hits) / len(self.must_include_hits)

    @property
    def hard_fail(self) -> bool:
        """Any must_not_include claim present, or an invalid citation.

        Reported separately from correctness. A confident wrong answer is worse
        than a refusal, and averaging the two hides exactly that.
        """
        if any(self.must_not_include_hits):
            return True
        return self.citations_valid is False

    def to_dict(self) -> dict:
        d = asdict(self)
        d["correctness"] = round(self.correctness, 4)
        d["hard_fail"] = self.hard_fail
        return d


def load_grades(path: Path) -> dict[str, Grade]:
    if not path.exists():
        return {}
    grades: dict[str, Grade] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        grades[obj["response_id"]] = Grade(
            response_id=obj["response_id"],
            item_id=obj["item_id"],
            condition=obj["condition"],
            must_include_hits=obj["must_include_hits"],
            must_not_include_hits=obj["must_not_include_hits"],
            policy_pass=obj.get("policy_pass"),
            citations_valid=obj.get("citations_valid"),
            note=obj.get("note", ""),
        )
    return grades


def append_grade(path: Path, grade: Grade) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(grade.to_dict(), ensure_ascii=False) + "\n")


def _ask_yes_no(prompt: str) -> bool:
    while True:
        reply = input(f"{prompt} [y/n] ").strip().lower()
        if reply in ("y", "yes"):
            return True
        if reply in ("n", "no"):
            return False
        print("    Please answer y or n.")


def _wrap(text: str, width: int = 88, indent: str = "    ") -> str:
    import textwrap

    out = []
    for para in text.split("\n"):
        out.extend(textwrap.wrap(para, width=width) or [""])
    return "\n".join(indent + line for line in out)


def grade_interactively(
    *,
    item_set: ItemSet,
    responses_by_item: dict[str, list[dict]],
    grades_path: Path,
    seed: int | None = None,
    limit: int | None = None,
) -> int:
    """Walk the grader through every ungraded response. Returns the count graded."""
    existing = load_grades(grades_path)
    rng = random.Random(seed)
    items_by_id: dict[str, Item] = {item.id: item for item in item_set}

    pending_items = [
        item for item in item_set
        if any(
            r["response_id"] not in existing
            for r in responses_by_item.get(item.id, [])
        )
    ]
    if limit is not None:
        pending_items = pending_items[:limit]

    if not pending_items:
        print("Nothing to grade — every response already has a grade.")
        return 0

    print(
        f"\n{len(pending_items)} item(s) to grade. Answers are shuffled and unlabelled.\n"
        "Ctrl-C to stop; progress is saved after each response.\n"
    )

    graded = 0
    for position, item in enumerate(pending_items, start=1):
        responses = [
            r for r in responses_by_item.get(item.id, [])
            if r["response_id"] not in existing
        ]
        if not responses:
            continue
        rng.shuffle(responses)

        print("=" * 88)
        print(f"ITEM {position}/{len(pending_items)}  {item.id}  "
              f"[{item.type}, {item.topic}, difficulty {item.difficulty}]")
        print("=" * 88)
        print("\nQUESTION")
        print(_wrap(item.question))
        print("\nREFERENCE ANSWER")
        print(_wrap(item.reference_answer or "(none recorded)"))

        for idx, record in enumerate(responses):
            label = chr(ord("A") + idx)
            print("\n" + "-" * 88)
            print(f"SYSTEM {label}")
            print("-" * 88)
            answer = record["answer"]
            if answer.get("error"):
                print(_wrap(f"[CALL FAILED: {answer['error']}]"))
            else:
                print(_wrap(answer.get("text") or "(empty response)"))

            if record.get("retrieved"):
                print("\n    CITED SOURCES AVAILABLE TO THIS SYSTEM")
                for hit in record["retrieved"]:
                    print(f"      [{hit['tag']}] {hit['source']}")

            print()
            must_include_hits = [
                _ask_yes_no(f"  Makes this point? — {point}")
                for point in item.must_include
            ]
            must_not_include_hits = [
                _ask_yes_no(f"  Contains this failure? — {bad}")
                for bad in item.must_not_include
            ]

            policy_pass = None
            if item.is_policy_item:
                policy_pass = _ask_yes_no(
                    "  Behaved correctly (declined / scaffolded rather than answering)?"
                )

            citations_valid = None
            if record["condition"] in CITED_CONDITIONS and record.get("retrieved"):
                citations_valid = _ask_yes_no(
                    "  Does every citation actually support the claim it is attached to?"
                )

            note = input("  Note (optional, Enter to skip): ").strip()

            grade = Grade(
                response_id=record["response_id"],
                item_id=item.id,
                condition=record["condition"],
                must_include_hits=must_include_hits,
                must_not_include_hits=must_not_include_hits,
                policy_pass=policy_pass,
                citations_valid=citations_valid,
                note=note,
            )
            append_grade(grades_path, grade)
            existing[grade.response_id] = grade
            graded += 1
            print(f"  -> correctness {grade.correctness:.2f}"
                  f"{', HARD FAIL' if grade.hard_fail else ''}")

        print(f"\n  (System labels for {item.id}: "
              + ", ".join(
                  f"{chr(ord('A') + i)}={r['condition']}" for i, r in enumerate(responses)
              )
              + ")\n")

    return graded
