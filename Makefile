.DEFAULT_GOAL := help
PY := .venv/bin/python
YM07 := .venv/bin/ym07
CHUNKS := corpus/processed/DEMO-chunks.jsonl

.PHONY: help setup demo items conditions dry baseline rag sweep variance grade report report-file clean distclean

help:  ## Show this help
	@echo "YM-07 benchmark harness"
	@echo ""
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) | awk -F':.*?## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Start with:  make demo"

setup: .venv/bin/ym07  ## Create the venv and install the package

.venv/bin/ym07: pyproject.toml
	python3 -m venv .venv
	.venv/bin/pip install --quiet --upgrade pip
	.venv/bin/pip install --quiet -e .
	@echo "Installed. Try: make demo"

$(CHUNKS): scripts/make_demo_corpus.py
	@python3 scripts/make_demo_corpus.py

demo: setup $(CHUNKS)  ## Narrated walkthrough — no API calls, nothing spent
	@./scripts/demo.sh

ingest: setup  ## Build the retrieval corpus from corpus/raw
	@$(YM07) ingest

items: setup  ## Validate the benchmark set and show coverage
	@$(YM07) items

conditions: setup  ## List the experimental conditions and what each varies
	@$(YM07) conditions

dry: setup $(CHUNKS)  ## Dry-run all three main conditions (no API calls)
	@$(YM07) run C0-baseline C1-prompted C2-rag --dry-run --chunks $(CHUNKS)

# --- these cost money and need ANTHROPIC_API_KEY --------------------------

baseline: setup  ## REAL RUN: C0 and C1 (the ungrounded controls)
	@$(YM07) run C0-baseline C1-prompted

rag: setup  ## REAL RUN: C2 (needs corpus/processed/chunks.jsonl)
	@$(YM07) run C2-rag

sweep: setup  ## REAL RUN: every condition, for the full results table
	@$(YM07) run C0-baseline C1-prompted C2-rag C3-money C3-effort-low C3-topk-3

variance: setup  ## REAL RUN: C0 three times, to measure run-to-run spread
	@$(YM07) run C0-baseline --repeats 3

frontier: setup  ## REAL RUN: the bare question to every other frontier model (needs their keys)
	@$(YM07) run C0-gpt C0-gemini C0-grok C0-deepseek

# --------------------------------------------------------------------------

grade: setup  ## Blind-grade collected responses (interactive, resumable)
	@$(YM07) grade

report: setup  ## Aggregate graded runs into markdown tables
	@$(YM07) report

report-file: setup  ## Same, written to runs/report.md
	@$(YM07) report --out runs/report.md

clean:  ## Delete run outputs (grades and items are kept)
	@rm -rf runs/*/ && echo "Cleared runs/"

distclean: clean  ## Also delete the venv and the demo corpus
	@rm -rf .venv src/*.egg-info $(CHUNKS) && echo "Cleared .venv and demo corpus"
