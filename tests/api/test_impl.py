import os
import unittest
import urllib.request
import httpretty

from eocdb_client.api.impl import _ApiImpl
from eocdb_client.configstore import MemConfigStore


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.api = _ApiImpl(config_store=MemConfigStore(server_url="http://test-server/"))
        self.test_data_dir = os.path.join(os.path.dirname(__file__), "..", "res", "input")
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    def test_upload_store_files_success(self):
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/store/upload",
                               status=200,
                               body=b'{"chl-s170604w.sub": {"status": "OK", "issues": []},'
                                    b' "chl-s170710w.sub": {"status": "OK", "issues": []}}')
        dataset_paths = [os.path.join(self.test_data_dir, "chl", "chl-s170604w.sub"),
                         os.path.join(self.test_data_dir, "chl", "chl-s170710w.sub")]
        doc_file_paths = [os.path.join(self.test_data_dir, "cal_files", "ac90194.060328"),
                          os.path.join(self.test_data_dir, "cal_files", "DI7125f.cal"),
                          os.path.join(self.test_data_dir, "cal_files", "DI7125m.cal")]
        response = self.api.upload_datasets("a/p/c", dataset_paths, doc_file_paths)
        self.assertIsInstance(response, dict)
        self.assertEqual({'chl-s170604w.sub': {'issues': [], 'status': 'OK'},
                          'chl-s170710w.sub': {'issues': [], 'status': 'OK'}},
                         response)

    def test_upload_store_files_failure(self):
        httpretty.register_uri(httpretty.POST,
                               "http://test-server/eocdb/api/v0.1.0/store/upload",
                               status=400)
        dataset_paths = [os.path.join(self.test_data_dir, "chl", "chl-s170604w.sub"),
                         os.path.join(self.test_data_dir, "chl", "chl-s170710w.sub")]
        doc_file_paths = [os.path.join(self.test_data_dir, "cal_files", "ac90194.060328"),
                          os.path.join(self.test_data_dir, "cal_files", "DI7125f.cal"),
                          os.path.join(self.test_data_dir, "cal_files", "DI7125m.cal")]
        with self.assertRaises(urllib.request.HTTPError) as cm:
            self.api.upload_datasets("a/p/c", dataset_paths, doc_file_paths)
        self.assertEqual(400, cm.exception.code)
        self.assertEqual("Bad Request", cm.exception.reason)

    # def test_find_datasets(self):
    #     with self.assertRaises(urllib.error.HTTPError) as cm:
    #         self.api.find_datasets("a")
    #     self.assertEqual('HTTP Error 400: Resource not found:'
    #                      ' http://mock/eocdb/api/v0.1.0-dev.1/datasets?expr=a&offset=1&count=1000&format=json',
    #                      f'{cm.exception}')
    #
    #     result = self.api.find_datasets("empty")
    #     self.assertEqual(None, result)
    #
    #     result = self.api.find_datasets("ernie")
    #     self.assertEqual({'attribute_names': ['id', 'lon', 'lat', 'time', 'Chl_A'],
    #                       'data_records': [[23, 11.4, 52.1, '2016-05-01 10:54:26', 0.7],
    #                                        [24, 11.2, 52.2, '2016-05-01 11:12:19', 0.3]]}, result)
    #
    # def test_add_dataset(self):
    #     self.api.add_dataset("a")
    #
    # def test_delete_dataset(self):
    #     self.api.delete_dataset("a")

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
        api_with_defaults = _ApiImpl()
        self.assertIsNotNone(api_with_defaults.config)
        self.assertTrue(api_with_defaults.server_url is None
                        or api_with_defaults.server_url is not None)

    def test_make_url(self):
        api = _ApiImpl(config_store=MemConfigStore())
        with self.assertRaises(ValueError) as cm:
            api._make_url('/datasets')
        self.assertEqual('"server_url" is not configured', f'{cm.exception}')

        server_url_with_trailing_slash = 'http://localhost:2385/'
        api = _ApiImpl(config_store=MemConfigStore(server_url=server_url_with_trailing_slash))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('datasets'))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('/datasets'))

        server_url_without_trailing_slash = 'http://localhost:2385'
        api = _ApiImpl(config_store=MemConfigStore(server_url=server_url_without_trailing_slash))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('datasets'))
        self.assertEqual('http://localhost:2385/eocdb/api/v0.1.0/datasets', api._make_url('/datasets'))
