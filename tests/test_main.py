import subprocess
import sys
import unittest

from eocdb_client.main import main


class MainTest(unittest.TestCase):

    def test_run_module(self):
        with self.assertRaises(SystemExit):
            main(["--help"])

    def test_run_module_as_script(self):
        code = subprocess.run([sys.executable, __file__, "--help"]).returncode
        self.assertEquals(0, code)
