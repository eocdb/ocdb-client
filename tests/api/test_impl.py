import unittest
import urllib.error

from eocdb_client.api.impl import _ApiImpl
from eocdb_client.configstore import MemConfigStore
from tests.helpers import new_url_opener_mock

MOCK_SERVER_URL = "http://mock"
MOCK_SPEC = {
    "http://mock/eocdb/api/v0.1.0-dev.1/datasets?query=empty&index=0&results=100&format=json":
        'null',
    "http://mock/eocdb/api/v0.1.0-dev.1/datasets?query=ernie&index=0&results=100&format=json":
        '{'
        '  "attribute_names": ["id", "lon", "lat", "time", "Chl_A"], '
        '  "data_records": [[23, 11.4, 52.1, "2016-05-01 10:54:26", 0.7],'
        '                   [24, 11.2, 52.2, "2016-05-01 11:12:19", 0.3]]'
        '}',
    "http://mock/eocdb/api/v0.1.0-dev.1/datasets":
        '{'
        '  "attribute_names": ["id", "lon", "lat", "time", "Chl_A"], '
        '  "data_records": [[23, 11.4, 52.1, "2016-05-01 10:54:26", 0.7],'
        '                   [24, 11.2, 52.2, "2016-05-01 11:12:19", 0.3]]'
        '}',
}


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.api = _ApiImpl(config_store=MemConfigStore(),
                            server_url=MOCK_SERVER_URL,
                            url_opener=new_url_opener_mock(MOCK_SPEC))

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

    def test_find_datasets(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:
            self.api.find_datasets("a")
        self.assertEqual('HTTP Error 400: Resource not found:'
                         ' http://mock/eocdb/api/v0.1.0-dev.1/datasets?expr=a&offset=1&count=1000&format=json',
                         f'{cm.exception}')

        result = self.api.find_datasets("empty")
        self.assertEqual(None, result)

        result = self.api.find_datasets("ernie")
        self.assertEqual({'attribute_names': ['id', 'lon', 'lat', 'time', 'Chl_A'],
                          'data_records': [[23, 11.4, 52.1, '2016-05-01 10:54:26', 0.7],
                                           [24, 11.2, 52.2, '2016-05-01 11:12:19', 0.3]]}, result)

    def test_add_dataset(self):
        self.api.add_dataset("a")

    def test_delete_dataset(self):
        self.api.delete_dataset("a")

    def test_api_with_defaults(self):
        api_with_defaults = _ApiImpl()
        self.assertIsNotNone(api_with_defaults.config)
        self.assertTrue(api_with_defaults.server_url is None
                        or api_with_defaults.server_url is not None)

    def test_make_url(self):
        api = _ApiImpl(config_store=MemConfigStore())
        with self.assertRaises(ValueError) as cm:
            api._make_url('/eocdb/api/measurements')
        self.assertEqual('"server_url" is not configured', f'{cm.exception}')

        server_url_with_trailing_slash = 'http://localhost:2385/'
        api = _ApiImpl(config_store=MemConfigStore(server_url=server_url_with_trailing_slash))
        self.assertEqual('http://localhost:2385/eocdb/api/measurements', api._make_url('eocdb/api/measurements'))
        self.assertEqual('http://localhost:2385/eocdb/api/measurements', api._make_url('/eocdb/api/measurements'))

        server_url_without_trailing_slash = 'http://localhost:2385'
        api = _ApiImpl(config_store=MemConfigStore(server_url=server_url_without_trailing_slash))
        self.assertEqual('http://localhost:2385/eocdb/api/measurements', api._make_url('eocdb/api/measurements'))
        self.assertEqual('http://localhost:2385/eocdb/api/measurements', api._make_url('/eocdb/api/measurements'))
