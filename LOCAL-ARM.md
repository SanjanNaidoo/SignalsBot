# Running the open-weights arm on the gaming PC

Setup for the machine with the GPU (RTX 5070 Ti, 16 GB VRAM, 16 GB system RAM). Written
for a Windows machine with **nothing developer-related installed**. Every command is typed
into PowerShell; each step says what you should see if it worked.

**Why bother:** this arm costs nothing per run. The hosted models charge per question; a
model running on your own GPU does not. Prompt problems and broken benchmark items show up
here exactly as they would on a paid run, for free — so this is where to shake them out.

Budget about an hour, most of it downloads.

---

## How to open PowerShell

Press **Windows key + X**, then choose **Terminal** (on older Windows, **Windows
PowerShell**). A window with a blinking cursor opens. That is where every command below
goes: type it, press Enter.

To paste into it: **right-click** — Ctrl+V often does not work there.

---

## Step 1 — Install Python 3.12, and specifically 3.12

**The version matters more than anything else in this guide.** PyTorch publishes no
GPU builds for Python 3.13 or 3.14. On those versions the install silently gives you a
CPU-only PyTorch, which then fails with a baffling `cannot import name
'NP_SUPPORTED_MODULES'` error that looks like a broken project but is really a version
mismatch. Even if it loaded, it would ignore your GPU entirely.

The big yellow **Download Python** button on python.org gives you the *newest* release.
Do not use it. Instead:

1. Go to **python.org/downloads/windows**
2. Find the newest entry beginning **Python 3.12** — for example *Python 3.12.10*
3. Click its **Download Windows installer (64-bit)** link
4. Run it

> **Do not install Python from the Microsoft Store.** That version is sandboxed and breaks
> the virtual environment we create in step 4.

In the installer, on the very first screen:

**☑ Add python.exe to PATH** — tick this box. It is easy to miss and everything afterwards
fails without it.

Then click *Install Now*.

Check it worked — close PowerShell, open a fresh one, and run:

```powershell
py -3.12 --version
```

Expected: `Python 3.12.x`

Having other Python versions installed alongside is fine; they do not interfere. That is
why every command below says `py -3.12` rather than `py` — it picks the right one
explicitly.

---

## Step 2 — Install Git

Go to **git-scm.com/download/win**, run the installer, and accept every default.

Check:

```powershell
git --version
```

Expected: `git version 2.x.x`

---

## Step 3 — Check the graphics driver

```powershell
nvidia-smi
```

You should see a table with your card named in it. Top right reads **CUDA Version: 12.x**.

That number must be **12.8 or higher**. If it is lower, update your driver through GeForce
Experience or from nvidia.com, then reopen PowerShell and check again.

If `nvidia-smi` is not recognised at all, the driver is not installed properly — fix that
before continuing, because nothing below will work.

---

## Step 4 — Download the project and create its environment

```powershell
cd $HOME\Documents
git clone https://github.com/SanjanNaidoo/SignalsBot.git
cd SignalsBot
py -3.12 -m venv .venv
```

That last command makes a private Python environment inside the project, so nothing we
install pollutes the rest of your PC.

**Note the style of the commands from here on.** They all start `.venv\Scripts\`. That runs
the copy of Python inside the project directly. You may have seen guides that say to
"activate" the environment first — on Windows that runs into PowerShell's script-blocking
policy, so we skip it entirely and use full paths. Nothing is lost.

Check:

```powershell
.venv\Scripts\python.exe --version
```

Expected: `Python 3.12.x`

---

## Step 5 — Install PyTorch (the step that goes wrong)

Your 5070 Ti is a Blackwell card. The ordinary version of PyTorch has no code for it and
fails later with a confusing `no kernel image is available for execution on the device`
error that looks like a bug in the project but is not. So install the CUDA 12.8 build
explicitly, and do it **before** anything else:

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
```

This downloads roughly 2.5 GB. It will take a while.

**Now verify, and do not continue until this passes:**

```powershell
.venv\Scripts\python.exe -c "import torch; print(torch.__version__, '|', torch.version.cuda, '|', torch.cuda.is_available())"
```

Expected something like: `2.7.0+cu128 | 12.8 | True`

Three things to check in that line:

- the version ends **`+cu128`** — no suffix means a CPU-only build
- the middle value is a **CUDA version**, not `None`
- it ends **`True`**

If any of those is wrong, stop. See Troubleshooting. Every later step depends on this, and
carrying on produces confusing errors that look unrelated.

---

## Step 6 — Install the project

```powershell
.venv\Scripts\python.exe -m pip install -e ".[local]"
```

This adds the libraries that load and run the model. It will not replace the PyTorch you
just installed.

---

## Step 7 — Free checks, before any model downloads

None of these touch the GPU or the internet:

```powershell
.venv\Scripts\ym07.exe items
.venv\Scripts\ym07.exe conditions
.venv\Scripts\ym07.exe run C0-oss --dry-run
```

`items` should report **47 items** and digest `020975b2ecf884f4`. If the digest differs,
the question set on this machine is not the one used on the Mac, and results would not be
comparable — re-clone before going further.

`--dry-run` walks the whole pipeline with fake answers. If it completes, the plumbing is
sound and only the model itself is untested.

---

## Step 8 — The first real run

```powershell
.venv\Scripts\ym07.exe run C1-oss
```

The first time, this downloads the model — about 5.5 GB — into
`C:\Users\<you>\.cache\huggingface`. Make sure your C: drive has ~10 GB free. Later runs
reuse it and start immediately.

Then it answers all 47 questions. Expect several minutes.

To watch GPU memory while it runs, open a second PowerShell window and run:

```powershell
nvidia-smi -l 5
```

The model should occupy roughly 5–6 GB of your 16 GB, leaving plenty of headroom.

**Why `C1-oss` first:** it uses the course instructions but no course notes, so it needs
nothing beyond the repository. It is also the direct counterpart of the `C1-prompted` run
already done on Claude — same questions, same instructions, different model. That is the
comparison the project is about.

`C0-oss` (no instructions at all) is the other free run worth doing, and pairs with the
five `C0` runs already collected.

---

## Step 9 — Send the results back

Runs land in `runs\`. Ungrounded runs are committed to the repository, so:

```powershell
git add runs
git commit -m "Add C1-oss run from the local GPU"
git push
```

Then they appear on GitHub and can be pulled onto the Mac for grading alongside everything
else.

---

## Later: the course notes

Only needed if the retrieval conditions (`C2-oss`, `C2-oss-tuned`) go ahead — currently on
hold pending the supervisor. **Skip this section for now.**

When the time comes: the course material is deliberately not in the repository, because it
is copyright UCT and the repository is public. Copy `corpus\processed\chunks.jsonl` from
the Mac by hand (USB stick or cloud drive). Copying the processed file rather than
re-running the ingestion guarantees both machines retrieve from byte-identical text.

---

## Troubleshooting

**`py` or `git` is not recognised** — the installer did not add it to PATH. Reinstall
Python with the *Add python.exe to PATH* box ticked, and always reopen PowerShell after an
install; an already-open window keeps the old settings.

**`cannot import name 'NP_SUPPORTED_MODULES' from 'torch._dynamo.utils'`** — the classic
symptom of a CPU-only PyTorch sitting next to a `transformers` that expects the CUDA one.
Almost always caused by building the environment on Python 3.13 or 3.14, for which no GPU
wheels exist. Reinstalling the extra will not help. Fix it by rebuilding on 3.12:

```powershell
cd $HOME\Documents\SignalsBot
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
.venv\Scripts\python.exe -m pip install -e ".[local]"
```

Deleting `.venv` throws away only downloaded libraries. Your work, the questions and any
runs are untouched.

**`torch.cuda.is_available()` prints `False`** — either the driver is older than CUDA 12.8
(check `nvidia-smi`), or a CPU-only PyTorch got installed. Check which:

```powershell
.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.version.cuda)"
```

`torch.version.cuda` printing `None` means a CPU build. Redo it:

```powershell
.venv\Scripts\python.exe -m pip uninstall -y torch
.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
```

If that reports *no matching distribution*, your Python version has no GPU wheels — check
`.venv\Scripts\python.exe --version` and rebuild on 3.12 as above.

**`no kernel image is available for execution on the device`** — same cause: PyTorch
without Blackwell support. Fix as above.

**`CUDA out of memory`** — close games, browsers and anything else using the GPU, then
retry. If it persists, check `src\ym07\conditions.py` still names a model ending
`-bnb-4bit`; the full-size version will not fit.

**The process is killed while loading the model** — that is system RAM, not VRAM. Confirm
the model name ends `-bnb-4bit`. The compressed version streams to the GPU; the
uncompressed one needs more than your 16 GB.

**`bitsandbytes` errors on import** — this library is better tested on Linux than Windows.
If it will not cooperate, the fallback is to run the whole arm inside WSL2 (Windows
Subsystem for Linux) with GPU passthrough, which is a well-trodden path but a longer setup.
Ask before going down that road — there may be a simpler fix.

**Downloads are very slow** — the model is 5.5 GB and comes from Hugging Face. If it
stalls, Ctrl+C and rerun; it resumes rather than restarting.
