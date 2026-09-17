"""Read-only tool checks. Run from 00-setup: uv run python check_setup.py."""

import os
from pathlib import Path
import shutil
import subprocess
import sys


def check(label, command, hint):
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=45)
        output = (result.stdout or result.stderr).strip()
        if result.returncode == 0 and output:
            print(f"PASS  {label}: {output.splitlines()[0]}", flush=True)
            return True
    except (OSError, subprocess.TimeoutExpired):
        pass
    print(f"FAIL  {label}: {hint}", flush=True)
    return False


def main():
    print("DSO 576 setup check", flush=True)
    root = Path(__file__).resolve().parent.parent
    expected = root / ".venv"
    correct = Path(sys.prefix).resolve() == expected.resolve()
    print(f"{'PASS' if correct else 'FAIL'}  Shared course Python: {sys.executable}")
    if not correct:
        print('      From 00-setup, run: uv run --no-project --isolated --python ">=3.11" setup_course.py')
    results = [correct]
    for name, hint in (
        ("git", "Redo 'Install Git' in the setup guide."),
        ("gh", "Redo 'Install GitHub CLI' in the setup guide."),
        ("uv", "Redo 'Install uv' in the setup guide."),
        ("code", "Reopen your terminal. On Mac, in VS Code's Command Palette run 'Shell Command: Install code command in PATH'."),
        ("codex", "Install the Codex command-line tool from the setup guide; the VS Code extension alone is not the CLI."),
    ):
        command = shutil.which(name)
        if command:
            results.append(check(name, [command, "--version"], hint))
        else:
            print(f"FAIL  {name}: {hint}", flush=True)
            results.append(False)
    checks = (
        ("Python", "import sys; print(sys.version.split()[0])"),
        ("pandas", "import pandas; print(pandas.__version__)"),
        ("numpy", "import numpy; print(numpy.__version__)"),
        ("Streamlit", "import streamlit; print(streamlit.__version__)"),
        ("plotting", "import matplotlib, plotly, seaborn; print('matplotlib, plotly, seaborn')"),
        ("Altair", "import altair; print(altair.__version__)"),
        ("Excel", "import openpyxl, xlrd; print('openpyxl, xlrd')"),
        ("database", "from sqlalchemy import create_engine, text; e=create_engine('sqlite://'); print(e.connect().execute(text('select 1')).scalar())"),
        ("PostgreSQL drivers", "import psycopg2, psycopg; print('psycopg2, psycopg')"),
        ("web requests", "import requests; print(requests.__version__)"),
        ("notebook cells", "import ipykernel; print(ipykernel.__version__)"),
    )
    for label, code in checks:
        results.append(check(label, [sys.executable, "-c", code], "Run uv sync from the parent course folder, then retry."))
    kernel = (
        "from jupyter_client.kernelspec import KernelSpecManager; from pathlib import Path; import sys; "
        "actual=KernelSpecManager().get_kernel_spec('dso576').argv[0]; "
        "assert Path(actual).absolute()==Path(sys.argv[1]).absolute(), actual; print(actual)"
    )
    python = expected / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    results.append(check("DSO 576 kernel", [sys.executable, "-c", kernel, str(python)],
                         'From 00-setup, rerun: uv run --no-project --isolated --python ">=3.11" setup_course.py'))
    if all(results):
        print(f"\nALL CHECKS PASSED ({len(results)}/{len(results)}). Ready for DSO 576.")
        print("Open the parent course folder in VS Code; all weekly repos should be visible.")
        return 0
    print(f"\n{results.count(False)} check(s) failed. Follow the FAIL hints, reopen your terminal, then run:")
    print("  cd ~/dso576/00-setup\n  uv run python check_setup.py")
    print("Still failing? Send your instructor the full output, including the PASS lines.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
