# Running the open-weights arm

Setup for the machine with the GPU. The hosted arm is driven from anywhere; this arm needs
CUDA, so it runs on the desktop (RTX 5070 Ti, 16 GB VRAM, 16 GB system RAM).

**Why this arm matters beyond the results:** it costs nothing per run. Prompt defects and
broken benchmark items surface here identically to the hosted arm, for free. Debug here
first; spend on the hosted arm only once the prompt and item set have stopped changing.

## 0. Prerequisites

- **NVIDIA driver** recent enough for CUDA 12.8. Check with `nvidia-smi` — the top right
  reports the maximum CUDA version the driver supports; it must read 12.8 or higher.
- **Python 3.11, 3.12 or 3.13**, on PATH.
- **git**.
- ~15 GB free disk: about 6 GB for the model, the rest for wheels.

## 1. Clone

```bash
git clone https://github.com/SanjanNaidoo/SignalsBot.git
cd SignalsBot
```

## 2. Environment

Linux or WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

From here the docs write `ym07`; with the venv activated that resolves correctly on both
platforms. If you would rather not activate it, use `.venv/bin/ym07` on Linux or
`.venv\Scripts\ym07.exe` on Windows.

## 3. Install torch first, from the CUDA 12.8 index

**This step is the one that goes wrong.** The 5070 Ti is Blackwell (compute capability
sm_120). The default PyPI torch wheel has no kernels for it and fails at model load with a
`no kernel image is available for execution on the device` error. Install torch explicitly
before anything else:

```bash
pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cu128
```

Verify before continuing — this must print `True` and name the card:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Expected: `True NVIDIA GeForce RTX 5070 Ti`

If it prints `False`, stop and fix the driver or the wheel. Nothing below will work.

## 4. Install the harness

```bash
pip install -e ".[local]"
```

This pulls transformers, accelerate and bitsandbytes alongside the base package. It will
not reinstall torch, since the CUDA build is already present and satisfies the requirement.

## 5. Check the harness before touching the GPU

Free, no model download, no API calls:

```bash
ym07 items
ym07 conditions
ym07 run C0-oss --dry-run
```

`ym07 items` should report **47 items** and the digest recorded in `bench/schema.md`. If
the digest differs, the item set has changed and runs are not comparable across machines.

## 6. First real local run

```bash
ym07 run C1-oss
```

The first invocation downloads `unsloth/Qwen2.5-7B-Instruct-bnb-4bit`, roughly 5.5 GB, into
the HuggingFace cache. Subsequent runs reuse it.

`C1-oss` is the right first run: it uses the course prompt but **no retrieval**, so it does
not need the corpus, which is not in the repository. It is also the direct counterpart of
`C1-prompted` in the hosted arm.

Expect a few minutes for 47 items. Watch VRAM in another terminal with `nvidia-smi`; the
4-bit model should sit around 5–6 GB, leaving plenty of headroom.

## 7. Add the corpus, for the retrieval conditions

`C2-oss` needs the course material, which is **deliberately not in the repository** — it is
copyright UCT and gitignored. Copy it across from the Mac by hand:

- Copy the whole of `corpus/raw/` onto the PC, into `corpus/raw/`.
- Then rebuild the chunk file locally:

```bash
ym07 ingest
```

It should report **335 chunks from 109 files**. If the count differs, the corpora differ
between machines and any cross-machine comparison is invalid.

Alternatively copy `corpus/processed/chunks.jsonl` directly, which skips ingestion and
guarantees both machines retrieve from byte-identical chunks. That is the safer option
while results are being collected.

Then:

```bash
ym07 run C2-oss
```

## 8. What to look for

The point of this arm right now is **finding defects, not collecting results**. Read the
responses in `runs/<timestamp>-C1-oss/responses.jsonl` and check:

- Does it answer ordinary questions, rather than withholding them as assessed work?
- Does it decline the four `scope` items, without reciting the answer while declining?
- Does it treat the machine-learning topics as in scope? Part B is easy to get wrong.
- For `C2-oss`, does it cite `[S1]`-style tags, and do the cited passages actually support
  the claims?

Every defect found here is one that does not have to be found on a paid run.

## Troubleshooting

**`no kernel image is available for execution on the device`** — torch is not the CUDA 12.8
build. Redo step 3; `pip uninstall torch` first.

**`CUDA out of memory`** — something else is using the GPU, or the model loaded unquantized.
Confirm the model id in `src/ym07/conditions.py` still ends in `-bnb-4bit`.

**bitsandbytes fails to import on Windows** — its Windows support is less exercised than on
Linux. If it will not cooperate, run the whole arm inside WSL2 with CUDA passthrough, which
is the better-trodden path.

**Process killed while loading** — system RAM, not VRAM. Confirm you are using the
pre-quantized checkpoint rather than quantizing a bf16 model on load; 16 GB is not enough
for the latter.
