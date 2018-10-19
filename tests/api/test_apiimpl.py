import json
import urllib.request
from abc import ABCMeta

import httpretty

from eocdb_client.api.apiimpl import ApiImpl
from eocdb_client.configstore import MemConfigStore
from tests.helpers import ClientTest


class ApiTest(ClientTest, metaclass=ABCMeta):
    pass


class DatasetsApiTest(ApiTest):
    def test_upload_store_files(self):
        expected_response = {
            'chl-s170604w.sub': {'issues': [], 'status': 'OK'},
            'chl-s170710w.sub': {'issues': [], 'status': 'OK'}
        }
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/store/upload",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        dataset_paths = [self.get_input_path("chl", "chl-s170604w.sub"),
                         self.get_input_path("chl", "chl-s170710w.sub")]
        doc_file_paths = [self.get_input_path("cal_files", "ac90194.060328"),
                          self.get_input_path("cal_files", "DI7125f.cal"),
                          self.get_input_path("cal_files", "DI7125m.cal")]
        response = self.api.upload_datasets("BIGELOW/BALCH/gnats", dataset_paths, doc_file_paths)
        self.assertIsInstance(response, dict)
        self.assertEqual(expected_response, response)

        # Force failure
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/store/upload",
                               status=400)
        with self.assertRaises(urllib.request.HTTPError) as cm:
            self.api.upload_datasets("BIGELOW/BALCH/gnats", dataset_paths, doc_file_paths)
        self.assertEqual(400, cm.exception.code)
        self.assertEqual("Bad Request", cm.exception.reason)

    def test_find_datasets(self):
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
        response = self.api.find_datasets(expr="metadata.cruise:gnats")
        self.assertIsInstance(response, dict)
        self.assertEqual(expected_response, response)

    def test_validate_dataset(self):
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/datasets/validate",
                               status=200)
        self.api.validate_dataset(self.get_input_path("chl", "chl-s170604w.sub"))

    def test_add_datasets(self):
        httpretty.register_uri(httpretty.PUT,
                               "http://test-server/eocdb/api/v0.1.0/datasets",
                               status=200)
        self.api.add_dataset(self.get_input_path("chl", "chl-s170604w.sub"))

    def test_update_datasets(self):
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/datasets",
                               status=200)
        self.api.update_dataset(self.get_input_path("chl", "chl-s170604w.sub"))

    def test_delete_datasets(self):
        httpretty.register_uri(httpretty.DELETE,
                               "http://test-server/eocdb/api/v0.1.0/datasets/3",
                               status=200)
        self.api.delete_dataset(dataset_id="3")

        # Force failure
        httpretty.register_uri(httpretty.DELETE,
                               "http://test-server/eocdb/api/v0.1.0/datasets/4",
                               status=404)
        with self.assertRaises(urllib.request.HTTPError):
            self.api.delete_dataset(dataset_id="4")

    def test_get_dataset(self):
        expected_response = {
            "id": "245",
            "name": "chl/chl-s170604w.sub",
            "metadata": {},
            "records": [[]]
        }
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0/datasets/245",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        response = self.api.get_dataset(dataset_id="245")
        self.assertIsInstance(response, dict)
        self.assertEqual(expected_response, response)

        # Force failure
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0/datasets/246",
                               status=404)
        with self.assertRaises(urllib.request.HTTPError):
            self.api.get_dataset(dataset_id="246")

    def test_get_dataset_by_name(self):
        expected_response = {
            "id": "245",
            "name": "chl/chl-s170604w.sub",
            "metadata": {},
            "records": [[]]
        }
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0"
                               "/datasets/BIGELOW/BALCH/gnats/chl/chl-s170604w.sub",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        response = self.api.get_dataset_by_name(dataset_path="BIGELOW/BALCH/gnats/chl/chl-s170604w.sub")
        self.assertIsInstance(response, dict)
        self.assertEqual(expected_response, response)

        # Force failure
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0"
                               "/datasets/BIGELOW/BALCH/gnats/chl/chl-s170604w.sub",
                               status=404)
        with self.assertRaises(urllib.request.HTTPError):
            self.api.get_dataset_by_name(dataset_path="BIGELOW/BALCH/gnats/chl/chl-s170604w.sub")

    def test_list_datasets_in_path(self):
        expected_response = [
            {
                "id": "242",
                "name": "chl/chl-s170610w.sub",
                "metadata": {},
                "records": [[]]
            },
            {
                "id": "245",
                "name": "chl/chl-s170604w.sub",
                "metadata": {},
                "records": [[]]
            }
        ]
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0"
                               "/datasets/BIGELOW/BALCH/gnats",
                               status=200,
                               body=json.dumps(expected_response).encode("utf-8"))
        response = self.api.list_datasets_in_path(dataset_path="BIGELOW/BALCH/gnats")
        self.assertIsInstance(response, list)
        self.assertEqual(expected_response, response)

        # Force failure
        httpretty.register_uri(httpretty.GET,
                               "http://test-server/eocdb/api/v0.1.0"
                               "/datasets/IGELOW/ELCH/gnitz",
                               status=404)
        with self.assertRaises(urllib.request.HTTPError):
            self.api.list_datasets_in_path(dataset_path="IGELOW/ELCH/gnitz")


class ConfigApiTest(ApiTest):
    def test_set_get_config_value(self):
        with self.assertRaises(ValueError) as cm:
            self.api.set_config_param("bibo", 132)
        self.assertEqual('unknown configuration parameter "bibo"', f'{cm.exception}')

        self.api.set_config_param("server_url", 'http://bibo')
        self.assertEqual('http://bibo', self.api.get_config_param("server_url"))

    def test_server_url(self):
        with self.assertRaises(ValueError) as cm:
            self.api.server_url = None
        self.assertEqual('"server_url" must be specified', f'{cm.exception}')

        server_url = 'http://test:18432'
        self.api.server_url = server_url
        self.assertEqual(server_url, self.api.server_url)
        self.assertEqual(server_url, self.api.get_config_param('server_url'))

    def test_api_with_defaults(self):
        api_with_defaults = ApiImpl()
        self.assertIsNotNone(api_with_defaults.config)
        self.assertTrue(api_with_defaults.server_url is None
                        or api_with_defaults.server_url is not None)

    def test_make_url(self):
        api = ApiImpl(config_store=MemConfigStore())
        with self.assertRaises(ValueError) as cm:
            api._make_url('/datasets')
        self.assertEqual('"server_url" is not configured', f'{cm.exception}')

        server_url_with_trailing_slash = 'http://localhost:2385/'
        api = ApiImpl(config_store=MemConfigStore(server_url=server_url_with_trailing_slash))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('datasets'))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('/datasets'))

        server_url_without_trailing_slash = 'http://localhost:2385'
        api = ApiImpl(config_store=MemConfigStore(server_url=server_url_without_trailing_slash))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('datasets'))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('/datasets'))
