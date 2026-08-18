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
check "Codex (AI coding agent)"    "codex --version"        "redo the 'Set up your AI tools' step (install Codex)"

echo
if [ "$fail" -eq 0 ]; then
  echo "ALL CHECKS PASSED ($pass/$pass) — your laptop is ready for DSO-576."
else
  echo "$fail check(s) failed, $pass passed. Fix the FAIL lines above (each one names the setup step to redo), then run this again:"
  echo "  bash check_setup.sh"
  echo "Still stuck? Bring your laptop to office hours or the first class — we'll fix it together."
fi
