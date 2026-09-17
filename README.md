# DSO 576 laptop setup

Use **PowerShell on Windows** or **Terminal on macOS/Linux**. Install `uv` and
the other tools from the course app's [setup guide](https://dso576.vercel.app/setup)
first. No Bash or administrator access is needed for the commands below.

## 1. Create the parent course folder

```text
mkdir ~/dso576
cd ~/dso576
pwd
```

If the folder already exists, continue with `cd`. Keep **all weekly repos inside
this folder**. The installer also works if you gave your course folder another name.

## 2. Get this setup repo

```text
git clone https://github.com/pengshi-usc/00-setup.git
cd 00-setup
```

Already cloned it? Use these instead:

```text
cd ~/dso576/00-setup
git pull
```

## 3. Set up the shared Python environment once

Close VS Code and any running course Python programs, then run:

```text
uv run --no-project --isolated --python ">=3.11" setup_course.py
```

Wait for **SUCCESS**. This creates `pyproject.toml`, `uv.lock`, and `.venv` in
**the parent course folder**, checks Python, and registers the **DSO 576** kernel.
If you had an old `00-setup/.venv`, it removes it only after the new setup passes.
No separate `fix_python_path.py` step is needed. If a check fails, follow its
printed instructions and rerun the same command; coursework is preserved.

## 4. Check the installation

Still in `00-setup`, run:

```text
uv run hello.py
uv run python check_setup.py
```

Look for **SUCCESS** and **ALL CHECKS PASSED**. A FAIL line tells you what to fix.
Then try:

```text
uv run streamlit hello
```

If Streamlit asks for an email, leave it blank and press Enter. Once you see the
demo in your browser, press **Ctrl+C** in the terminal to stop it.

## 5. Open the whole course folder

```text
cd ..
code .
```

VS Code's Explorer should show `00-setup` alongside your weekly repos. Try a
Python cell. Only if asked for a kernel or the cell fails, choose **DSO 576**.
The installer prints the interpreter path and recovery steps if needed.

## Later weeks

This is a one-time setup. Future weekly repos inherit the parent project and
should not contain a separate `pyproject.toml`. From a weekly repo:

```text
uv sync
uv run python your_file.py
```

When instructed to add a package, use `uv add package-name`. If the repo supplies
a requirements file, use `uv add -r requirements.txt`. Both update the parent
project and the same environment; no new kernel registration is needed.

The old `check_setup.sh` only prints directions to the Python checker. It no
longer runs misleading tool checks inside Git Bash or WSL.
