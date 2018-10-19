import os
import unittest
from abc import ABCMeta, abstractmethod
from typing import Any, Dict

import httpretty

from eocdb_client.api.apiimpl import ApiImpl
from eocdb_client.configstore import MemConfigStore


class ClientTest(unittest.TestCase, metaclass=ABCMeta):

    def setUp(self):
        self.api = ApiImpl(**self.api_kwargs)
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

    @property
    def api_kwargs(self) -> Dict:
        return dict(config_store=MemConfigStore(server_url="http://test-server"))

    @classmethod
    def get_input_base_dir(cls) -> str:
        return os.path.join(os.path.dirname(__file__), "res", "input")

    @classmethod
    def get_input_path(cls, *components):
        return os.path.join(cls.get_input_base_dir(), *components)
