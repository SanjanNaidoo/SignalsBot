"""Command line entry point.

  ym07 items                     validate the benchmark set and show coverage
  ym07 conditions                list the experimental conditions
  ym07 run C0-baseline           run one condition (add --dry-run for no API calls)
  ym07 grade                     blind-grade the responses collected so far
  ym07 report                    aggregate graded runs into markdown tables
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from .conditions import CONDITIONS, get_condition, repeat
from .config import load_config
from .grading import grade_interactively, load_grades
from .items import coverage, load_items
from .model import build_client
from .report import breakdown, render, summarise
from .retrieval import build_retriever
from .runner import MissingCorpusError, discover_runs, load_run, run_condition

DEFAULT_CONFIG = "configs/eee4114f.yaml"
DEFAULT_ITEMS = "bench/eee4114f.seed.jsonl"
DEFAULT_CHUNKS = "corpus/processed/chunks.jsonl"
DEFAULT_RUNS = "runs"
DEFAULT_GRADES = "grades/grades.jsonl"


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--items", default=DEFAULT_ITEMS)


def cmd_items(args) -> int:
    config = load_config(args.config)
    item_set = load_items(args.items, known_topics=config.topic_ids)
    stats = coverage(item_set)

    print(f"{item_set.path}  —  {len(item_set)} items, digest {item_set.digest}\n")
    for heading in ("topic", "type", "difficulty"):
        print(f"  by {heading}:")
        for key in sorted(stats[heading]):
            print(f"    {key:<24} {stats[heading][key]}")
        print()

    missing = sorted(config.topic_ids - set(stats["topic"]))
    if missing:
        print(f"  topics with no items: {', '.join(missing)}")
    return 0


def cmd_conditions(args) -> int:
    config = load_config(args.config)
    for name in sorted(CONDITIONS):
        condition = CONDITIONS[name]
        print(f"{name}")
        print(f"  {condition.description}")
        print(f"  model={condition.resolved_model(config)} "
              f"effort={condition.resolved_effort(config)} "
              f"prompt={'yes' if condition.use_course_prompt else 'no'} "
              f"retrieval={'top_k=' + str(condition.resolved_top_k(config)) if condition.use_retrieval else 'no'}")
        print(f"  {condition.purpose}\n")
    return 0


def cmd_run(args) -> int:
    config = load_config(args.config)
    item_set = load_items(args.items, known_topics=config.topic_ids)
    retriever = build_retriever(args.chunks)

    # One client per provider, built on first use and reused. A sweep can mix the
    # hosted and open arms, and loading a local model is slow enough that it must
    # not happen once per condition.
    clients: dict[str, object] = {}

    def client_for(condition) -> object:
        provider = condition.resolved_provider(config)
        if provider not in clients:
            clients[provider] = build_client(args.dry_run, provider, config)
        return clients[provider]

    if args.dry_run:
        print("DRY RUN — no model will be called and no money will be spent.\n")

    for name in args.conditions:
        base = get_condition(name)
        for index in range(1, args.repeats + 1):
            condition = base if args.repeats == 1 else repeat(base, index)
            print(f"{condition.name}  ({condition.description})")
            try:
                run_dir = run_condition(
                    condition=condition,
                    config=config,
                    item_set=item_set,
                    client=client_for(condition),
                    retriever=retriever,
                    runs_dir=Path(args.runs),
                    workers=args.workers,
                    dry_run=args.dry_run,
                )
            except MissingCorpusError as exc:
                print(f"  skipped: {exc}\n", file=sys.stderr)
                break
            manifest = json.loads((run_dir / "manifest.json").read_text())
            print(f"  -> {run_dir}  "
                  f"cost ${manifest['total_cost_usd']:.4f}  "
                  f"errors {manifest['errors']}  refusals {manifest['refusals']}\n")
    return 0


def _collect_runs(runs_dir: Path, only: list[str] | None):
    runs = []
    for run_dir in discover_runs(runs_dir):
        manifest, records = load_run(run_dir)
        if only and manifest["condition"] not in only:
            continue
        runs.append((manifest, records))
    return runs


def cmd_grade(args) -> int:
    config = load_config(args.config)
    item_set = load_items(args.items, known_topics=config.topic_ids)
    runs = _collect_runs(Path(args.runs), args.conditions)

    if not runs:
        print("No runs found. Run a condition first.", file=sys.stderr)
        return 1

    if any(m.get("dry_run") for m, _ in runs) and not args.allow_dry_run:
        print(
            "Refusing to grade: dry-run output is present, and grading placeholder "
            "text produces meaningless numbers. Re-run for real, or pass "
            "--allow-dry-run to rehearse the grading flow.",
            file=sys.stderr,
        )
        return 1

    digests = {m["items_digest"] for m, _ in runs}
    if len(digests) > 1:
        print(
            "Warning: these runs used different item sets. They are not comparable "
            "and the report must not present them side by side.\n",
            file=sys.stderr,
        )

    responses_by_item = defaultdict(list)
    for _, records in runs:
        for record in records:
            responses_by_item[record["item_id"]].append(record)

    graded = grade_interactively(
        item_set=item_set,
        responses_by_item=responses_by_item,
        grades_path=Path(args.grades),
        seed=args.seed,
        limit=args.limit,
    )
    print(f"\nGraded {graded} response(s). Saved to {args.grades}")
    return 0


def cmd_report(args) -> int:
    config = load_config(args.config)
    item_set = load_items(args.items, known_topics=config.topic_ids)
    runs = _collect_runs(Path(args.runs), args.conditions)
    if not runs:
        print("No runs found.", file=sys.stderr)
        return 1

    grades = load_grades(Path(args.grades))
    text = render(
        summaries=summarise(runs=runs, grades=grades),
        breakdowns={
            key: breakdown(runs=runs, grades=grades, item_set=item_set, key=key)
            for key in ("type", "topic", "difficulty")
        },
        item_set=item_set,
    )
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ym07", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("items", help="validate the benchmark set and show coverage")
    _common(p); p.set_defaults(func=cmd_items)

    p = sub.add_parser("conditions", help="list the experimental conditions")
    _common(p); p.set_defaults(func=cmd_conditions)

    p = sub.add_parser("run", help="run one or more conditions")
    _common(p)
    p.add_argument("conditions", nargs="+", choices=sorted(CONDITIONS))
    p.add_argument("--chunks", default=DEFAULT_CHUNKS)
    p.add_argument("--runs", default=DEFAULT_RUNS)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--repeats", type=int, default=1,
                   help="run each condition N times to measure run-to-run variance")
    p.add_argument("--dry-run", action="store_true",
                   help="exercise the pipeline without calling the API")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("grade", help="blind-grade collected responses")
    _common(p)
    p.add_argument("--runs", default=DEFAULT_RUNS)
    p.add_argument("--grades", default=DEFAULT_GRADES)
    p.add_argument("--conditions", nargs="*", default=None)
    p.add_argument("--limit", type=int, default=None, help="grade at most N items")
    p.add_argument("--seed", type=int, default=None, help="fix the shuffle for reproducibility")
    p.add_argument("--allow-dry-run", action="store_true")
    p.set_defaults(func=cmd_grade)

    p = sub.add_parser("report", help="aggregate graded runs")
    _common(p)
    p.add_argument("--runs", default=DEFAULT_RUNS)
    p.add_argument("--grades", default=DEFAULT_GRADES)
    p.add_argument("--conditions", nargs="*", default=None)
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_report)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted — progress saved", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
