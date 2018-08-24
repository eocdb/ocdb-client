import unittest

from click.testing import CliRunner

from eocdb_client.api import Api
from eocdb_client.cli import cli


class CliTest(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_config(self):
        result = self.runner.invoke(cli, ['conf', 'server_url', "http://localhost:4000"], obj=Api())
        self.assertEqual(0, result.exit_code)
        self.assertEqual("", result.output)
