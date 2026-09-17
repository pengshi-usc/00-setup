import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('setup_course', Path(__file__).resolve().parents[1] / 'setup_course.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='DSO course with spaces ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.old = self.root / '00-setup' / '.venv'
        self.old.mkdir(parents=True)
        (self.old / 'pyvenv.cfg').write_text('home = /old/python\n')
        (self.root / '00-setup' / 'pyproject.toml').write_text('[project]\nname="setup"\nversion="1.0"\nrequires-python=">=3.11"\ndependencies=["pandas", "ipykernel"]\n')
        self.week = self.root / '05-encode'
        self.week.mkdir()

    def test_fresh_install_needs_no_legacy_environment(self):
        setup.shutil.rmtree(self.old)
        with patch.object(setup, 'run'):
            setup.migrate(self.root)
        manifest = setup.read_project(self.root / 'pyproject.toml')
        self.assertIn('00-setup', manifest['tool']['uv']['workspace']['members'])
        self.assertIn('02-trace*', manifest['tool']['uv']['workspace']['members'])
        self.assertFalse(self.old.exists())

    def test_detection_root_repo_and_wrong_folder(self):
        self.assertEqual(setup.find_root(self.root), self.root)
        self.assertEqual(setup.find_root(self.week), self.root)
        with self.assertRaises(RuntimeError):
            setup.find_root(self.root / '05-encode' / 'deeper')

    def test_manifest_preserves_edits_on_rerun_and_adds_members(self):
        p, content = setup.prepare_manifest(self.root, ['00-setup'])
        p.write_text(content.replace('"pandas",', '"pandas", "requests",'))
        _, updated = setup.prepare_manifest(self.root, ['00-setup', '02-trace'])
        data = setup.tomllib.loads(updated)
        self.assertIn('requests', data['project']['dependencies'])
        self.assertEqual(data['tool']['uv']['workspace']['members'], ['00-setup', '02-trace'])

    def test_existing_unowned_manifest_is_untouched(self):
        p = self.root / 'pyproject.toml'
        p.write_text('[project]\nname="mine"\n')
        with self.assertRaises(RuntimeError):
            setup.prepare_manifest(self.root, ['00-setup'])
        self.assertEqual(p.read_text(), '[project]\nname="mine"\n')

    def test_failed_sync_keeps_old_environment(self):
        with patch.object(setup, 'run', side_effect=subprocess.CalledProcessError(1, ['uv', 'sync'])):
            with self.assertRaises(subprocess.CalledProcessError):
                setup.migrate(self.root)
        self.assertTrue((self.old / 'pyvenv.cfg').exists())

    def test_kernel_failure_keeps_old_environment(self):
        def fail_kernel(args, *_):
            if 'install' in args:
                raise subprocess.CalledProcessError(1, args)
        with patch.object(setup, 'run', side_effect=fail_kernel):
            with self.assertRaises(subprocess.CalledProcessError):
                setup.migrate(self.root)
        self.assertTrue(self.old.exists())

    def test_success_deletes_only_old_environment(self):
        work = self.week / 'my_work.py'
        work.write_text('print("keep")')
        with patch.object(setup, 'run'):
            setup.migrate(self.root)
            setup.migrate(self.root)
        self.assertFalse(self.old.exists())
        self.assertEqual(work.read_text(), 'print("keep")')

    def test_environment_override_is_rejected(self):
        with patch.dict(os.environ, {'UV_PROJECT_ENVIRONMENT': '/elsewhere'}):
            with self.assertRaises(RuntimeError):
                setup.migrate(self.root)
        self.assertTrue(self.old.exists())
        self.assertFalse((self.root / 'pyproject.toml').exists())

    def test_linked_old_environment_is_rejected(self):
        setup.shutil.rmtree(self.old)
        self.old.symlink_to(self.week, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            setup.migrate(self.root)
        self.assertTrue(self.week.exists())

    def test_locked_old_environment_can_be_cleaned_on_retry(self):
        (self.old / 'lib').mkdir()
        with patch.object(setup, 'run'), patch.object(setup.shutil, 'rmtree', side_effect=PermissionError('file in use')):
            with self.assertRaisesRegex(RuntimeError, 'Close VS Code'):
                setup.migrate(self.root)
        self.assertTrue((self.old / 'pyvenv.cfg').exists())
        with patch.object(setup, 'run'):
            setup.migrate(self.root)
        self.assertFalse(self.old.exists())

    def test_download_error_explains_recovery(self):
        result = subprocess.CompletedProcess([], 1, '', 'network unavailable')
        with patch.object(setup.subprocess, 'run', return_value=result):
            with self.assertRaisesRegex(RuntimeError, 'Check your internet connection'):
                setup.run(['uv', 'sync'], self.root, {})


if __name__ == '__main__':
    unittest.main()
