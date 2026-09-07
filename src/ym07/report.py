"""Aggregate graded runs into the tables the report needs.

Per-condition headline numbers, then breakdowns by item type and topic. The
breakdowns matter: a system can score well overall while failing every
error_finding item, and that difference is the interesting result.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .grading import Grade
from .items import ItemSet


@dataclass
class Summary:
    condition: str
    n_graded: int
    n_responses: int
    mean_correctness: float
    hard_fail_rate: float
    policy_pass_rate: float | None
    citation_valid_rate: float | None
    cost_usd: float
    dry_run: bool


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarise(
    *,
    runs: list[tuple[dict, list[dict]]],
    grades: dict[str, Grade],
) -> list[Summary]:
    summaries: list[Summary] = []

    for manifest, records in runs:
        condition = manifest["condition"]
        graded = [grades[r["response_id"]] for r in records if r["response_id"] in grades]

        policy = [g.policy_pass for g in graded if g.policy_pass is not None]
        cites = [g.citations_valid for g in graded if g.citations_valid is not None]

        summaries.append(
            Summary(
                condition=condition,
                n_graded=len(graded),
                n_responses=len(records),
                mean_correctness=_mean([g.correctness for g in graded]),
                hard_fail_rate=_mean([1.0 if g.hard_fail else 0.0 for g in graded]),
                policy_pass_rate=_mean([1.0 if p else 0.0 for p in policy]) if policy else None,
                citation_valid_rate=_mean([1.0 if c else 0.0 for c in cites]) if cites else None,
                cost_usd=manifest.get("total_cost_usd", 0.0),
                dry_run=manifest.get("dry_run", False),
            )
        )

    summaries.sort(key=lambda s: s.condition)
    return summaries


def breakdown(
    *,
    runs: list[tuple[dict, list[dict]]],
    grades: dict[str, Grade],
    item_set: ItemSet,
    key: str,
) -> dict[str, dict[str, float]]:
    """Mean correctness per condition, split by 'type', 'topic' or 'difficulty'."""
    attr = {"type": "type", "topic": "topic", "difficulty": "difficulty"}[key]
    item_key = {item.id: str(getattr(item, attr)) for item in item_set}

    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for _, records in runs:
        for record in records:
            grade = grades.get(record["response_id"])
            if grade is None:
                continue
            bucket = item_key.get(record["item_id"], "?")
            buckets[bucket][record["condition"]].append(grade.correctness)

    return {
        bucket: {cond: _mean(vals) for cond, vals in by_cond.items()}
        for bucket, by_cond in buckets.items()
    }


def _table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i])
        for i in range(len(headers))
    ]
    def line(cells): return "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " |"
    out = [line(headers), "|" + "|".join("-" * (w + 2) for w in widths) + "|"]
    out += [line(row) for row in rows]
    return "\n".join(out)


def render(
    *,
    summaries: list[Summary],
    breakdowns: dict[str, dict[str, dict[str, float]]],
    item_set: ItemSet,
) -> str:
    out: list[str] = ["# Benchmark results", ""]

    if any(s.dry_run for s in summaries):
        out += [
            "> **DRY RUN DATA PRESENT.** One or more runs below called no model. "
            "These numbers are placeholders and must not be reported.",
            "",
        ]

    ungraded = [s for s in summaries if s.n_graded < s.n_responses]
    if ungraded:
        out += [
            "> Incomplete grading: "
            + ", ".join(f"{s.condition} ({s.n_graded}/{s.n_responses})" for s in ungraded)
            + ".",
            "",
        ]

    out += ["## Headline", ""]
    out.append(
        _table(
            ["Condition", "Graded", "Correctness", "Hard fail", "Policy", "Citations", "Cost USD"],
            [
                [
                    s.condition,
                    f"{s.n_graded}/{s.n_responses}",
                    f"{s.mean_correctness:.3f}",
                    f"{s.hard_fail_rate:.3f}",
                    "—" if s.policy_pass_rate is None else f"{s.policy_pass_rate:.3f}",
                    "—" if s.citation_valid_rate is None else f"{s.citation_valid_rate:.3f}",
                    f"{s.cost_usd:.4f}",
                ]
                for s in summaries
            ],
        )
    )

    for key, title in (("type", "By item type"), ("topic", "By topic"), ("difficulty", "By difficulty")):
        data = breakdowns.get(key) or {}
        if not data:
            continue
        conditions = sorted({c for by_cond in data.values() for c in by_cond})
        out += ["", f"## {title}", ""]
        out.append(
            _table(
                [key.capitalize()] + conditions,
                [
                    [bucket] + [
                        f"{data[bucket][c]:.3f}" if c in data[bucket] else "—"
                        for c in conditions
                    ]
                    for bucket in sorted(data)
                ],
            )
        )

    out += [
        "",
        "## Reading this",
        "",
        "- **Correctness** is the fraction of `must_include` points made, averaged over items.",
        "- **Hard fail** is the rate of answers containing a known failure or an invalid "
        "citation. It is reported separately, never averaged into correctness.",
        "- **Policy** covers `scope` and `integrity` items only — behaviour, judged apart "
        "from factual accuracy.",
        f"- Item set: {item_set.path.name}, {len(item_set)} items, digest `{item_set.digest}`.",
        "",
    ]
    return "\n".join(out)
