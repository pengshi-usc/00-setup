"""Run: uv run --no-project --isolated --python ">=3.11" setup_course.py

Install the shared course environment in the parent folder.
Standard library only for the bootstrap; also repairs the old nested layout.
"""

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tomllib


MARKER = "# DSO 576 shared Python environment\n"
LEGACY_MARKER = "# Created by DSO 576 setup_course.py\n"
MEMBERS = "# BEGIN DSO 576 workspace members\n"
END_MEMBERS = "# END DSO 576 workspace members\n"


def read_project(path):
    return tomllib.loads(path.read_text(encoding="utf-8"))


def find_root(cwd):
    for candidate in (cwd, cwd.parent):
        if (candidate / "00-setup" / "pyproject.toml").is_file():
            return candidate.resolve()
    raise RuntimeError(
        "Cannot find 00-setup/pyproject.toml. Run this command from your course "
        "folder (the one containing 00-setup), or from a repo directly inside it."
    )


def workspace_projects(root):
    projects = []
    for folder in sorted(root.iterdir()):
        if folder.name.startswith(".") or not folder.is_dir():
            continue
        manifest = folder / "pyproject.toml"
        if not manifest.is_file():
            continue
        if folder.is_symlink():
            raise RuntimeError(f"{folder}: linked project folders are not supported.")
        data = read_project(manifest)
        if "project" not in data or "workspace" in data.get("tool", {}).get("uv", {}):
            raise RuntimeError(f"{manifest}: this project needs a separate workspace. Ask for help before continuing.")
        projects.append(folder.name)
    # Old published week 02 has its own manifest. A glob may match no directory
    # yet, so it joins this workspace automatically when cloned later.
    return [name for name in projects if name != "02-trace"] + ["02-trace*"]


def prepare_manifest(root, projects):
    path = root / "pyproject.toml"
    block = MEMBERS + "[tool.uv.workspace]\nmembers = " + json.dumps(projects) + "\n" + END_MEMBERS
    if path.exists():
        old = path.read_text(encoding="utf-8")
        if old.startswith(LEGACY_MARKER):
            old = MARKER + old[len(LEGACY_MARKER):]
        if not old.startswith(MARKER) or old.count(MEMBERS) != 1 or old.count(END_MEMBERS) != 1:
            raise RuntimeError(f"{path} already exists and was not created by this script. It has not been overwritten; ask for help merging it.")
        before, rest = old.split(MEMBERS)
        _, after = rest.split(END_MEMBERS)
        content = before + block + after
    else:
        source = read_project(root / "00-setup" / "pyproject.toml")["project"]
        dependencies = list(source.get("dependencies", []))
        if not any(dep.lower().startswith("ipykernel") for dep in dependencies):
            dependencies.append("ipykernel>=6.29")
        content = (
            MARKER + "# Shared environment for all repos in this course folder.\n"
            "[project]\nname = \"dso576-shared\"\nversion = \"1.0.0\"\n"
            + "requires-python = " + json.dumps(source.get("requires-python", ">=3.11")) + "\n"
            + "dependencies = " + json.dumps(dependencies, indent=4) + "\n\n"
            + "[tool.uv]\npackage = false\n\n" + block
        )
    tomllib.loads(content)
    return path, content


def run(args, cwd, env):
    result = subprocess.run(
        list(map(str, args)), cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace",
    )
    if result.returncode:
        detail = "\n".join((result.stderr or result.stdout).strip().splitlines()[-10:])
        if "sync" in args:
            advice = "Package installation failed. Check your internet connection and rerun. If the message says 'No solution found', send the message to your instructor."
        elif "install" in args:
            advice = "Could not register the notebook kernel. Close VS Code and all notebooks, then rerun."
        else:
            advice = "The new Python environment did not pass its check. Send the message below to your instructor."
        raise RuntimeError(f"{advice}\nFolder: {cwd}\nDetails:\n{detail}")


def migrate(root):
    uv = shutil.which("uv")
    if not uv:
        raise RuntimeError("uv is not available. Reopen your terminal after installing uv, then try again.")
    for variable in ("UV_PROJECT_ENVIRONMENT", "UV_WORKING_DIRECTORY", "UV_PROJECT"):
        if os.environ.get(variable):
            raise RuntimeError(f"{variable} is set and overrides project discovery. Unset it in this terminal, then try again.")
    legacy = root / "00-setup" / ".venv"
    target = root / ".venv"
    for folder in (legacy, target):
        if folder.is_symlink() or (folder.exists() and getattr(folder.lstat(), "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT):
            raise RuntimeError(f"{folder} is a link; ask for help before continuing.")
        if folder.exists() and not (folder / "pyvenv.cfg").is_file():
            raise RuntimeError(f"{folder} does not look like a virtual environment. It has not been changed.")
    # Never remove an environment that is running this installer.
    if Path(sys.prefix).resolve() == legacy.resolve():
        raise RuntimeError("This script is running inside the old environment. Close the terminal, open a fresh terminal, then use the documented setup command.")
    projects = workspace_projects(root)
    path, content = prepare_manifest(root, projects)
    path.write_text(content, encoding="utf-8")
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    print(f"Course folder: {root}", flush=True)
    print("1/3 Installing course packages (the first run may take a few minutes)...", flush=True)
    run([uv, "sync", "--all-packages"], root, env)
    python = target / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    # Check package health and ordinary project discovery before touching the old venv.
    print("2/3 Checking packages and Python in your course folders...", flush=True)
    run([uv, "pip", "check", "--python", python], root, env)
    probe = (
        "import pathlib,sys,pandas,ipykernel; "
        "assert pathlib.Path(sys.prefix).resolve() == pathlib.Path(sys.argv[1]).resolve(), sys.executable; "
        "print(sys.executable)"
    )
    folders = [root] + [p for p in sorted(root.iterdir()) if p.is_dir() and not p.name.startswith(".")]
    for folder in folders:
        if not folder.is_symlink():
            run([uv, "run", "python", "-c", probe, target], folder, env)
    # Replaces the same dso576 kernel students registered during initial setup.
    print("3/3 Updating the DSO 576 notebook/Interactive kernel...", flush=True)
    run([python, "-m", "ipykernel", "install", "--user", "--name", "dso576", "--display-name", "DSO 576"], root, env)
    run([python, "-c",
         "from jupyter_client.kernelspec import KernelSpecManager; import sys; "
         "from pathlib import Path; "
         "actual = KernelSpecManager().get_kernel_spec('dso576').argv[0]; "
         "assert Path(actual).absolute() == Path(sys.argv[1]).absolute(), actual",
         python], root, env)
    if legacy.exists():
        print(f"Removing the old environment: {legacy}", flush=True)
        try:
            # Keep the venv marker until last so a Windows file-lock failure
            # leaves a recognizable environment that the next run can clean up.
            for item in legacy.iterdir():
                if item.name == "pyvenv.cfg":
                    continue
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            (legacy / "pyvenv.cfg").unlink()
            legacy.rmdir()
        except OSError as exc:
            raise RuntimeError(
                "The new environment works, but the old .venv could not be fully removed. "
                "Close VS Code, notebooks, and terminals using the old Python, then rerun this command. "
                f"Details: {exc}"
            ) from exc
    print("\nSUCCESS: packages work, course folders share Python, and the DSO 576 kernel is updated.")
    print(f"Python: {python}")
    print("\nNext: close old VS Code windows, then run these lines here:")
    if Path.cwd().resolve() != root:
        print("  cd ..")
    print("  code .")
    print("If 'code' is not recognized: open VS Code > File > Open Folder and choose:")
    print(f"  {root}")
    print("Try running a cell in Interactive/notebooks; VS Code should find the new environment.")
    print("Only if asked for a kernel or the cell fails: Select Kernel > Jupyter Kernels > DSO 576.")
    print("If VS Code still uses 00-setup: run 'Python: Select Interpreter' from the")
    print("Command Palette (Cmd+Shift+P on Mac; Ctrl+Shift+P on Windows/Linux),")
    print("then 'Enter interpreter path' and paste the Python path above.")
    print("\nNext time, from any course repo: uv run python your_file.py")
    print("For future weekly repos, uv sync uses this same environment; no new kernel setup is needed.")
    print("Quick check (should print the shared Python path, without 00-setup):")
    print('  uv run python -c "import pandas, sys; print(sys.executable)"')


def main():
    try:
        migrate(find_root(Path.cwd()))
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"\nSETUP STOPPED: {exc}", file=sys.stderr)
        print("\nFirst check your location with:\n  pwd\n  ls", file=sys.stderr)
        print("You should see 00-setup, or be inside a repo next to it (use cd .. to go up).", file=sys.stderr)
        print("Then rerun the same setup command. If it still fails, send your instructor", file=sys.stderr)
        print("the SETUP STOPPED message and the output of pwd and ls. Your coursework is preserved.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
