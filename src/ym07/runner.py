"""Run one condition over the frozen item set.

Every run writes a directory containing the raw responses and a manifest. The
manifest records the config digest, the item-set digest and the resolved model
settings, so any number in the report can be traced to the exact inputs that
produced it — and so two runs can be checked for comparability rather than
assumed comparable.
"""

from __future__ import annotations

import json
import platform
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .conditions import Condition
from .config import CourseConfig
from .items import Item, ItemSet
from .model import Answer
from .prompts import system_prompt, user_prompt
from .retrieval import LexicalRetriever


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


class MissingCorpusError(RuntimeError):
    pass


def run_condition(
    *,
    condition: Condition,
    config: CourseConfig,
    item_set: ItemSet,
    client,
    retriever: LexicalRetriever | None,
    runs_dir: Path,
    workers: int = 4,
    dry_run: bool = False,
    progress=print,
) -> Path:
    if condition.use_retrieval and retriever is None:
        raise MissingCorpusError(
            f"{condition.name} needs a corpus, but corpus/processed/chunks.jsonl is "
            "empty or missing. Ingest the course material first, or run an "
            "ungrounded condition (C0-baseline, C1-prompted)."
        )

    model_id = condition.resolved_model(config)
    effort = condition.resolved_effort(config)
    top_k = condition.resolved_top_k(config)
    system = system_prompt(config, grounded=condition.use_retrieval) if condition.use_course_prompt else None

    run_dir = runs_dir / f"{_timestamp()}-{condition.name}"
    run_dir.mkdir(parents=True, exist_ok=True)

    def answer_one(item: Item) -> dict:
        hits = retriever.search(item.question, top_k) if condition.use_retrieval else []
        user = user_prompt(item.question, hits)
        answer: Answer = client.answer(
            system=system,
            user=user,
            model=model_id,
            max_tokens=config.model.max_tokens,
            effort=effort,
        )
        return {
            "response_id": f"{run_dir.name}::{item.id}",
            "item_id": item.id,
            "topic": item.topic,
            "type": item.type,
            "difficulty": item.difficulty,
            "condition": condition.name,
            "question": item.question,
            "retrieved": [
                {
                    "tag": f"S{i}",
                    "chunk_id": hit.chunk.chunk_id,
                    "source": hit.chunk.citation(),
                    "score": round(hit.score, 4),
                }
                for i, hit in enumerate(hits, start=1)
            ],
            "answer": answer.to_dict(),
        }

    records: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done, record in enumerate(pool.map(answer_one, item_set.items), start=1):
            records.append(record)
            err = record["answer"].get("error")
            flag = " ERROR" if err else ""
            progress(f"  [{done}/{len(item_set)}] {record['item_id']}{flag}")

    records.sort(key=lambda r: r["item_id"])
    with (run_dir / "responses.jsonl").open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    errors = [r for r in records if r["answer"].get("error")]
    refusals = [r for r in records if r["answer"].get("stop_reason") == "refusal"]
    total_cost = sum(r["answer"]["cost_usd"] for r in records)

    manifest = {
        "condition": condition.name,
        "description": condition.description,
        "purpose": condition.purpose,
        "dry_run": dry_run,
        "started_utc": run_dir.name.split("-")[0],
        "ym07_version": __version__,
        "python": platform.python_version(),
        "config_path": str(config.path),
        "config_digest": config.digest,
        "items_path": str(item_set.path),
        "items_digest": item_set.digest,
        "item_count": len(item_set),
        "model": model_id,
        "provider": condition.resolved_provider(config),
        "effort": effort,
        "max_tokens": config.model.max_tokens,
        "use_course_prompt": condition.use_course_prompt,
        "use_retrieval": condition.use_retrieval,
        "top_k": top_k if condition.use_retrieval else None,
        "corpus_chunks": len(retriever) if retriever else 0,
        "errors": len(errors),
        "refusals": len(refusals),
        "total_cost_usd": round(total_cost, 4),
        "total_input_tokens": sum(r["answer"]["input_tokens"] for r in records),
        "total_output_tokens": sum(r["answer"]["output_tokens"] for r in records),
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    if system:
        (run_dir / "system_prompt.txt").write_text(system, encoding="utf-8")

    if errors:
        print(
            f"  {len(errors)} item(s) failed — see responses.jsonl. Do not grade an "
            "incomplete run without noting it.",
            file=sys.stderr,
        )
    return run_dir


def load_run(run_dir: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in (run_dir / "responses.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return manifest, records


def discover_runs(runs_dir: Path) -> list[Path]:
    return sorted(
        p for p in runs_dir.iterdir()
        if p.is_dir() and (p / "manifest.json").exists()
    )
