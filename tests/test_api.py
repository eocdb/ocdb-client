import unittest

from eocdb_client.api import Api


class ApiTest(unittest.TestCase):
    def test_config(self):
        Api().config("a", "b")

    def test_query(self):
        Api().query("a")

    def test_add(self):
        Api().add("a")

    def test_remove(self):
        Api().remove("a")
