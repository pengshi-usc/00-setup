"""Real installation test; temp files and isolated kernel registry, no user venv edits.

Run: uv run --no-project --isolated --python ">=3.11" tests/integration_setup.py
Needs network/package cache and the tools from the course setup guide.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    source = Path(__file__).resolve().parents[1]
    root = Path(tempfile.mkdtemp(prefix='DSO fresh course with spaces ')).resolve()
    setup = root / '00-setup'
    setup.mkdir()
    for name in ('pyproject.toml', 'uv.lock', 'setup_course.py', 'check_setup.py', 'hello.py'):
        shutil.copy(source / name, setup / name)
    subprocess.run(['git', 'init', '-q', str(setup)], check=True)
    env = {k: v for k, v in os.environ.items() if k not in ('VIRTUAL_ENV', 'PYTHONPATH', 'PYTHONHOME')}
    env['JUPYTER_DATA_DIR'] = str(root / '.test-jupyter')

    def run(args, cwd):
        subprocess.run(args, cwd=cwd, env=env, check=True)

    # Exact student command, both supported launch locations, fresh then restart.
    run(['uv', 'run', '--no-project', '--isolated', '--python', '>=3.11', 'setup_course.py'], setup)
    # A restarting student may still have the old venv in 00-setup.
    run(['uv', 'venv', str(setup / '.venv')], root)
    run(['uv', 'run', '--no-project', '--isolated', '--python', '>=3.11', 'setup_course.py'], setup)
    run(['uv', 'run', '--no-project', '--isolated', '--python', '>=3.11', '00-setup/setup_course.py'], root)
    assert not (setup / '.venv').exists()
    python = root / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    kernel = json.loads((root / '.test-jupyter/kernels/dso576/kernel.json').read_text())
    assert kernel['argv'][0] == str(python)
    run(['uv', 'run', 'hello.py'], setup)
    run(['uv', 'run', 'python', 'check_setup.py'], setup)

    probe = 'import sys,pandas; from pathlib import Path; assert Path(sys.prefix).resolve()==Path(sys.argv[1]).resolve(); print(sys.executable)'
    # Existing published week 02 can be cloned AFTER setup, without rerunning it.
    week2 = root / '02-trace'
    week2.mkdir()
    (week2 / 'pyproject.toml').write_text('[project]\nname="harbor-house-front-office"\nversion="0.1.0"\nrequires-python=">=3.11"\ndependencies=["pandas", "ipykernel"]\n')
    run(['git', 'init', '-q'], week2)
    run(['uv', 'sync'], week2)
    run(['uv', 'run', 'python', '-c', probe, str(root / '.venv')], week2)
    assert not (week2 / '.venv').exists()
    # Future weeks use parent-only metadata and add requirements to that project.
    week = root / '05-example'
    week.mkdir()
    run(['git', 'init', '-q'], week)
    (week / 'requirements.txt').write_text('humanize\n')
    run(['uv', 'add', '-r', 'requirements.txt'], week)
    run(['uv', 'sync'], week)
    run(['uv', 'run', 'python', '-c', probe + '; import humanize', str(root / '.venv')], week)
    assert not (week / '.venv').exists()
    assert not (week / 'pyproject.toml').exists()
    # Launch the actual registered kernel as VS Code Interactive would.
    code = """
from jupyter_client import KernelManager
km = KernelManager(kernel_name='dso576')
km.start_kernel()
c = km.client()
c.start_channels()
try:
    c.wait_for_ready(timeout=30)
    mid = c.execute('import pandas,sys; from pathlib import Path; assert Path(sys.prefix).resolve() == Path(' + repr(sys.argv[1]) + ').resolve()')
    while True:
        reply = c.get_shell_msg(timeout=30)
        if reply['parent_header'].get('msg_id') == mid:
            assert reply['content']['status'] == 'ok', reply
            break
finally:
    c.stop_channels()
    km.shutdown_kernel(now=True)
print('PASS: headless registered notebook kernel')
"""
    run([str(python), '-c', 'import sys\n' + code, str(root / '.venv')], week)
    print('INTEGRATION PASSED:', root)


if __name__ == '__main__':
    main()
