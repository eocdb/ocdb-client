import unittest
from typing import List

from click.testing import CliRunner

from eocdb_client.api.impl import _ApiImpl
from eocdb_client.cli import cli
from eocdb_client.configstore import MemConfigStore
from tests.api.test_impl import MOCK_SERVER_URL, MOCK_SPEC
from tests.helpers import new_url_opener_mock


class CliTest(unittest.TestCase):

    def setUp(self):
        self.api = _ApiImpl(config_store=MemConfigStore(server_url=MOCK_SERVER_URL),
                            url_opener=new_url_opener_mock(MOCK_SPEC))

    def _invoke_cli(self, args: List[str]):
        runner = CliRunner()
        return runner.invoke(cli, args, obj=self.api)

    def test_license(self):
        result = self._invoke_cli(['--license'])
        # TODO: forman - fix me, we currently get "Error: Missing command."
        # self.assertEqual(0, result.exit_code)
        # self.assertEqual("", result.output)

    def test_config(self):
        result = self._invoke_cli(['conf', 'server_url', "https://biboserver1"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("", result.output)

        result = self._invoke_cli(['conf', 'server_url'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual('{\n'
                         '  "server_url": "https://biboserver1"\n'
                         '}\n',
                         result.output)

        result = self._invoke_cli(['conf'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual('{\n'
                         '  "server_url": "https://biboserver1"\n'
                         '}\n',
                         result.output)

    def test_server_url_option(self):
        result = self._invoke_cli(['--server_url', "https://biboserver2", "conf"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual('{\n'
                         '  "server_url": "https://biboserver2"\n'
                         '}\n',
                         result.output)

    def test_ds_find(self):
        result = self._invoke_cli(['ds', 'find', 'a'])
        self.assertEqual(-1, result.exit_code)
        self.assertEqual("",
                         result.output)

        result = self._invoke_cli(['ds', 'find', 'empty'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("(None, None, None)\n"
                         "No results.\n",
                         result.output)

        result = self._invoke_cli(['ds', 'find', 'ernie'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("(None, None, None)\n"
                         "{'attribute_names': ['id', 'lon', 'lat', 'time', 'Chl_A'], "
                         "'data_records': [[23, 11.4, 52.1, '2016-05-01 10:54:26', 0.7], "
                         "[24, 11.2, 52.2, '2016-05-01 11:12:19', 0.3]]}\n",
                         result.output)

    # def test_ds_add(self):
    #     result = self._invoke_cli(['ds', 'add', 'test.xls'])
    #     self.assertEqual(-1, result.exit_code)
    #     self.assertEqual("",
    #                      result.output)
    #
    # def test_ds_delete(self):
    #     result = self._invoke_cli(['ds', 'del', 'f612e4a0'])
    #     self.assertEqual(-1, result.exit_code)
    #     self.assertEqual("",
    #                      result.output)
