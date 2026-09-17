import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('checker', Path(__file__).resolve().parents[1] / 'check_setup.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CheckerTests(unittest.TestCase):
    def test_nonzero_exit_is_failure_even_with_version_output(self):
        result = subprocess.CompletedProcess([], 1, 'Python 3.12', '')
        with patch.object(checker.subprocess, 'run', return_value=result):
            self.assertFalse(checker.check('Python', ['python', '-V'], 'reopen terminal'))

    def test_missing_executable_and_timeout_are_failures(self):
        for error in (FileNotFoundError(), subprocess.TimeoutExpired(['code'], 45)):
            with patch.object(checker.subprocess, 'run', side_effect=error):
                self.assertFalse(checker.check('code', ['code', '--version'], 'reopen terminal'))

    def test_windows_command_path_with_spaces_is_one_argument(self):
        exe = r'C:\Program Files\Microsoft VS Code\bin\code.cmd'
        result = subprocess.CompletedProcess([], 0, '1.0\n', '')
        with patch.object(checker.subprocess, 'run', return_value=result) as run:
            self.assertTrue(checker.check('code', [exe, '--version'], 'reopen terminal'))
        self.assertEqual(run.call_args.args[0], [exe, '--version'])
        self.assertNotIn('shell', run.call_args.kwargs)


if __name__ == '__main__':
    unittest.main()
