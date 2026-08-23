#!/usr/bin/env bash
# DSO-576 setup checker. Run with:  bash check_setup.sh
# Checks every tool the course needs and prints PASS/FAIL for each.
# Safe to run as many times as you like — it only LOOKS, it changes nothing.

pass=0
fail=0

check() {
  # check "<label>" "<command to try>" "<hint if missing>"
  local label="$1" cmd="$2" hint="$3"
  if out=$(eval "$cmd" 2>/dev/null | head -1) && [ -n "$out" ]; then
    printf 'PASS  %-28s %s\n' "$label" "$out"
    pass=$((pass+1))
  else
    printf 'FAIL  %-28s -> %s\n' "$label" "$hint"
    fail=$((fail+1))
  fi
}

echo "DSO-576 setup check"
echo "==================="

check "git (version control)"      "git --version"          "redo the 'Install the core software' step for git"
check "gh (GitHub tool)"           "gh --version"           "redo the 'Install the core software' step for gh"
check "uv (Python manager)"        "uv --version"           "redo the 'Set up Python' step (install uv)"
check "Python via uv"              "uv run python -V"       "run 'uv sync' in this folder first, then try again"
check "pandas via uv"              "uv run python -c 'import pandas; print(\"pandas\", pandas.__version__)'" "run 'uv sync' in this folder first, then try again"
check "streamlit via uv"           "uv run streamlit version"  "run 'uv sync' in this folder first, then try again"
check "plotting (matplotlib+)"     "uv run python -c 'import matplotlib, plotly, seaborn; print(\"matplotlib\", matplotlib.__version__, \"plotly\", plotly.__version__, \"seaborn\", seaborn.__version__)'" "run 'uv sync' in this folder first, then try again"
check "plotting (altair)"          "uv run python -c 'import altair; print(\"altair\", altair.__version__)'" "run 'uv sync' in this folder first, then try again"
check "Excel readers"              "uv run python -c 'import openpyxl, xlrd; print(\"openpyxl\", openpyxl.__version__, \"xlrd\", xlrd.__version__)'" "run 'uv sync' in this folder first, then try again"
check "numpy via uv"               "uv run python -c 'import numpy; print(\"numpy\", numpy.__version__)'" "run 'uv sync' in this folder first, then try again"
check "database (SQLAlchemy)"      "uv run python -c 'import sqlalchemy; from sqlalchemy import create_engine, text; e = create_engine(\"sqlite://\"); print(\"sqlalchemy\", sqlalchemy.__version__, \"query:\", e.connect().execute(text(\"select 1\")).scalar())'" "run 'uv sync' in this folder first, then try again"
check "PostgreSQL drivers"         "uv run python -c 'import psycopg2, psycopg; print(\"psycopg2\", psycopg2.__version__, \"+ psycopg\", psycopg.__version__)'" "run 'uv sync' in this folder first, then try again"
check "requests (web)"             "uv run python -c 'import requests; print(\"requests\", requests.__version__)'" "run 'uv sync' in this folder first, then try again"
check "notebook cells (ipykernel)" "uv run python -c 'import ipykernel; print(\"ipykernel\", ipykernel.__version__)'" "run 'uv sync' in this folder first, then try again"
check "VS Code 'code' command"     "code --version"         "close this window and open a new one first; if it still fails see 'the setup check says FAIL for the code command' on the course Help page"
# The Codex CLI is NOT the VS Code Codex extension (2026-08-22). Students
# install the extension from the Marketplace, see the Codex icon appear in
# VS Code, and reasonably conclude they are done — then this line FAILs and
# the old hint ("install Codex") told them to do the thing they just did.
# Name the distinction in the label, the hint, and the footer below.
codex_before=$fail
check "Codex CLI (not extension)"  "codex --version"        "the VS Code Codex EXTENSION is not this — install the command-line tool too (see the note below)"
[ "$fail" -gt "$codex_before" ] && codex_missing=1

if [ -n "$codex_missing" ]; then
  echo
  echo "About the Codex CLI line above"
  echo "------------------------------"
  echo "Installing the Codex EXTENSION in VS Code does NOT give you the codex"
  echo "command. They are two separate installs and the course uses both:"
  echo "  - the VS Code extension = the Codex panel inside the editor"
  echo "  - the command-line tool = the 'codex' command in this window"
  echo "If you already see a Codex icon in VS Code, you have the extension;"
  echo "you still need the command-line tool. Install it with the line for"
  echo "your computer, then CLOSE this window and open a new one before"
  echo "running this check again (a window older than the install cannot see"
  echo "the new command):"
  echo "  macOS / Linux:  curl -fsSL https://chatgpt.com/codex/install.sh | sh"
  echo "  Windows:        run this in PowerShell, not here:"
  echo '                  powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"'
  echo "This is the 'Install the Codex command-line tool' step in the setup"
  echo "guide. If it still fails after reopening, see 'codex: command not"
  echo "found' on the course Help page."
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "ALL CHECKS PASSED ($pass/$pass) — your laptop is ready for DSO-576."
else
  echo "$fail check(s) failed, $pass passed. Fix the FAIL lines above (each one names the setup step to redo), then run this again:"
  echo "  bash check_setup.sh"
  echo "Still stuck? Bring your laptop to office hours or the first class — we'll fix it together."
fi
