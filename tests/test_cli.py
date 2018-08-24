import unittest

from click.testing import CliRunner

from eocdb_client.cli import cli


class CliTest(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_config(self):
        result = self.runner.invoke(cli, ['config', 'pi', '3.1415'], obj={})
        self.assertEqual(0, result.exit_code)
        self.assertEqual("config name, value: pi 3.1415\n", result.output)
