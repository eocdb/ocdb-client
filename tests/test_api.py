import unittest

from eocdb_client.api import Api


class ApiTest(unittest.TestCase):
    def test_set_get_config_value(self):
        api = Api()
        api.set_config_param("server_url", "http://localhost:4000")
        self.assertEqual("http://localhost:4000", api.get_config_param("server_url"))

    def test_query_measurements(self):
        with self.assertRaises(ValueError) as cm:
            Api().query_measurements("a")
        self.assertEqual('"server_url" is not configured', f'{cm.exception}')

    def test_add_measurements(self):
        Api().add_measurements("a")

    def test_remove_measurements(self):
        Api().remove_measurements("a")
