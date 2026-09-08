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

## Step 1 — Install Python

Go to **python.org/downloads** and get **Python 3.12** (not 3.13 — some of the libraries
we need do not publish 3.13 builds yet).

> **Do not install Python from the Microsoft Store.** That version is sandboxed and breaks
> the virtual environment we create in step 4. Use the installer from python.org.

In the installer, on the very first screen:

**☑ Add python.exe to PATH** — tick this box. It is easy to miss and everything afterwards
fails without it.

Then click *Install Now*.

Check it worked — close PowerShell, open a fresh one, and run:

```powershell
py --version
```

Expected: `Python 3.12.x`

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
py -m venv .venv
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
.venv\Scripts\python.exe -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Expected: `True NVIDIA GeForce RTX 5070 Ti`

If it prints `False`, the GPU is not visible to PyTorch. See Troubleshooting — do not carry
on, because every later step depends on this.

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

**`torch.cuda.is_available()` prints `False`** — either the driver is older than CUDA 12.8
(check `nvidia-smi`), or the wrong PyTorch got installed. To redo it:

```powershell
.venv\Scripts\python.exe -m pip uninstall -y torch
.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu128
```

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
