import tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from flask import Flask
from reliabackend.executions import compile_grc_file

class CompilationTests(unittest.TestCase):
    def check_build(self,exit_code):
        with tempfile.TemporaryDirectory() as root:
            filename=Path(root)/'receiver.grc';filename.write_text('source')
            cache=filename.with_suffix('.py');cache.write_text('old build')
            def process(command,directory):
                (Path(directory)/'target_file.py').write_text('new build')
                return Mock(returncode=exit_code,communicate=lambda timeout:('',''))
            with Flask(__name__).app_context(),patch('reliabackend.executions.GrcManager'),patch('reliabackend.executions.run_in_sandbox',side_effect=process):
                result=compile_grc_file(str(filename))
            return result,cache.read_text() if cache.exists() else None
    def test_failed_compile_discards_stale_and_partial_python(self):
        result,cache=self.check_build(1)
        self.assertFalse(result);self.assertIsNone(cache)
    def test_successful_compile_replaces_cached_python(self):
        result,cache=self.check_build(0)
        self.assertTrue(result);self.assertEqual(cache,'new build')

if __name__=='__main__':unittest.main()
