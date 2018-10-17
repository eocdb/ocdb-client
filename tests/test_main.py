import unittest

from eocdb_client.main import main


class MainTest(unittest.TestCase):

    def test_run_module(self):
        with self.assertRaises(SystemExit):
            main(['--help'])
