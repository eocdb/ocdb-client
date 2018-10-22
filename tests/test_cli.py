import json
from abc import ABCMeta
from typing import List, Dict

import httpretty
from click.testing import CliRunner

from eocdb_client.cli import cli
from eocdb_client.configstore import MemConfigStore
from eocdb_client.version import LICENSE_TEXT
from tests.helpers import ClientTest


class CliTest(ClientTest, metaclass=ABCMeta):

    def invoke_cli(self, args: List[str]):
        runner = CliRunner()
        return runner.invoke(cli, args, obj=self.api)


class CliDatasetTest(CliTest):

    def test_ds_upl(self):
        expected_response = {
            'chl-s170604w.sub': {'issues': [], 'status': 'OK'},
        }
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/store/upload",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        dataset_file = self.get_input_path("chl", "chl-s170604w.sub")
        doc_file_1 = self.get_input_path("cal_files", "DI7125f.cal")
        doc_file_2 = self.get_input_path("cal_files", "DI7125m.cal")
        result = self.invoke_cli(["ds", "upl", "BIGELOW/BALCH/gnats",
                                  dataset_file, "-d", doc_file_1, "-d", doc_file_2])
        self.assertEqual('{\n'
                         '  "chl-s170604w.sub": {\n'
                         '    "issues": [],\n'
                         '    "status": "OK"\n'
                         '  }\n'
                         '}\n',
                         result.output)
        self.assertEqual(0, result.exit_code)

        result = self.invoke_cli(["ds", "upl", "BIGELOW/BALCH/gnats",
                                  "-d", doc_file_1, "-d", doc_file_2])
        self.assertEqual("Error: At least a single <dataset-file> must be given.\n", result.output)
        self.assertEqual(1, result.exit_code)

    def test_ds_validate(self):
        expected_response = {
            'chl-s170604w.sub': {'issues': [], 'status': 'OK'},
        }
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/datasets/validate",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        dataset_file = self.get_input_path("chl", "chl-s170604w.sub")
        result = self.invoke_cli(["ds", "val", dataset_file])
        self.assertEqual('{\n'
                         '  "chl-s170604w.sub": {\n'
                         '    "issues": [],\n'
                         '    "status": "OK"\n'
                         '  }\n'
                         '}\n',
                         result.output)
        self.assertEqual(0, result.exit_code)

    def test_ds_add(self):
        httpretty.register_uri(httpretty.PUT,
                               "http://test-server/eocdb/api/v0.1.0/datasets",
                               status=200)
        dataset_file = self.get_input_path("chl", "chl-s170604w.sub")
        result = self.invoke_cli(["ds", "add", dataset_file])
        self.assertEqual("", result.output)
        self.assertEqual(0, result.exit_code)

    def test_ds_upd(self):
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/datasets",
                               status=200)
        dataset_file = self.get_input_path("chl", "chl-s170604w.sub")
        result = self.invoke_cli(["ds", "upd", dataset_file])
        self.assertEqual("", result.output)
        self.assertEqual(0, result.exit_code)

    def test_ds_del(self):
        httpretty.register_uri(httpretty.DELETE,
                               "http://test-server/eocdb/api/v0.1.0/datasets/a298f4576e2",
                               status=200)
        result = self.invoke_cli(["ds", "del", "a298f4576e2"])
        self.assertEqual("", result.output)
        self.assertEqual(0, result.exit_code)

    def test_ds_get(self):
        expected_response = {
            "metadata": dict(fields="a,b,c", units="m/s,m/s,m/s"),
            "records": [[1.3, 2.4, 3.5], [2.3, 3.4, 4.5], [3.3, 4.4, 5.5]]
        }
        expected_output = ('{\n'
                           '  "metadata": {\n'
                           '    "fields": "a,b,c",\n'
                           '    "units": "m/s,m/s,m/s"\n'
                           '  },\n'
                           '  "records": [\n'
                           '    [\n'
                           '      1.3,\n'
                           '      2.4,\n'
                           '      3.5\n'
                           '    ],\n'
                           '    [\n'
                           '      2.3,\n'
                           '      3.4,\n'
                           '      4.5\n'
                           '    ],\n'
                           '    [\n'
                           '      3.3,\n'
                           '      4.4,\n'
                           '      5.5\n'
                           '    ]\n'
                           '  ]\n'
                           '}\n')
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0/datasets/BIGELOW/BALCH/gnats/chl-s170604w.sub",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        result = self.invoke_cli(["ds", "get", "-p", "BIGELOW/BALCH/gnats/chl-s170604w.sub"])
        self.assertEqual(expected_output, result.output)
        self.assertEqual(0, result.exit_code)

        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0/datasets/34986752749",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        result = self.invoke_cli(["ds", "get", "--id", "34986752749"])
        self.assertEqual(expected_output, result.output)
        self.assertEqual(0, result.exit_code)

        result = self.invoke_cli(["ds", "get"])
        self.assertEqual("Error: Either <id> or <path> must be given.\n", result.output)
        self.assertEqual(1, result.exit_code)

    def test_ds_list(self):
        expected_response = {
            "totalCount": 2,
            "query": {"expr": "metadata.cruise:gnats"},
            "datasets": [
                {"id": "1", "path": "BIGELOW/BALCH/gnats", "name": "chl-s170604w.sub"},
                {"id": "2", "path": "BIGELOW/BALCH/gnats", "name": "chl-s170710w.sub"}
            ]
        }
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0/datasets/BIGELOW/BALCH/gnats",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        result = self.invoke_cli(["ds", "list", "BIGELOW/BALCH/gnats"])
        self.assertEqual('{\n'
                         '  "totalCount": 2,\n'
                         '  "query": {\n'
                         '    "expr": "metadata.cruise:gnats"\n'
                         '  },\n'
                         '  "datasets": [\n'
                         '    {\n'
                         '      "id": "1",\n'
                         '      "path": "BIGELOW/BALCH/gnats",\n'
                         '      "name": "chl-s170604w.sub"\n'
                         '    },\n'
                         '    {\n'
                         '      "id": "2",\n'
                         '      "path": "BIGELOW/BALCH/gnats",\n'
                         '      "name": "chl-s170710w.sub"\n'
                         '    }\n'
                         '  ]\n'
                         '}\n',
                         result.output)
        self.assertEqual(0, result.exit_code)

    def test_ds_find(self):
        expected_response = {
            "totalCount": 2,
            "query": {"expr": "metadata.cruise:gnats"},
            "datasets": [
                {"id": "1", "path": "BIGELOW/BALCH/gnats", "name": "chl-s170604w.sub"},
                {"id": "2", "path": "BIGELOW/BALCH/gnats", "name": "chl-s170710w.sub"}
            ]
        }
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0/datasets?expr=metadata.cruise:gnats",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        result = self.invoke_cli(["ds", "find", "--expr=metadata.cruise:gnats"])
        self.assertEqual('{\n'
                         '  "totalCount": 2,\n'
                         '  "query": {\n'
                         '    "expr": "metadata.cruise:gnats"\n'
                         '  },\n'
                         '  "datasets": [\n'
                         '    {\n'
                         '      "id": "1",\n'
                         '      "path": "BIGELOW/BALCH/gnats",\n'
                         '      "name": "chl-s170604w.sub"\n'
                         '    },\n'
                         '    {\n'
                         '      "id": "2",\n'
                         '      "path": "BIGELOW/BALCH/gnats",\n'
                         '      "name": "chl-s170710w.sub"\n'
                         '    }\n'
                         '  ]\n'
                         '}\n',
                         result.output)
        self.assertEqual(0, result.exit_code)


class CliConfigTest(CliTest):

    @property
    def api_kwargs(self) -> Dict:
        # Overridden to NOT specify 'server_url'!
        return dict(config_store=MemConfigStore())

    def test_license(self):
        result = self.invoke_cli(['lic'])
        self.assertEqual(LICENSE_TEXT + "\n", result.output)
        self.assertEqual(0, result.exit_code)

    def test_config(self):
        result = self.invoke_cli(['conf', 'server_url', "https://biboserver1"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual("", result.output)

        result = self.invoke_cli(['conf', 'server_url'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual('{\n'
                         '  "server_url": "https://biboserver1"\n'
                         '}\n',
                         result.output)

        result = self.invoke_cli(['conf'])
        self.assertEqual(0, result.exit_code)
        self.assertEqual('{\n'
                         '  "server_url": "https://biboserver1"\n'
                         '}\n',
                         result.output)

    def test_server_url_option(self):
        result = self.invoke_cli(['--server', "https://biboserver2", "conf"])
        self.assertEqual(0, result.exit_code)
        self.assertEqual('{\n'
                         '  "server_url": "https://biboserver2"\n'
                         '}\n',
                         result.output)
