#!/usr/bin/env sh
# Compatibility notice for old handouts; no tool checks run in Bash/WSL.
cat <<'EOF'
The setup checker now uses Python on every operating system.
On Windows, open PowerShell (not WSL or Git Bash).
On macOS/Linux, use your normal Terminal.
Then run these lines:

  cd ~/dso576/00-setup
  git pull
  uv run --no-project --isolated --python ">=3.11" setup_course.py
  uv run python check_setup.py

The installer creates/repairs the shared parent environment once.
The Python checker prints PASS/FAIL for your native installation.
EOF
exit 1
