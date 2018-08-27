import unittest
import os
from eocdb_client.configstore import ConfigStore, MemConfigStore, JsonConfigStore


class ConfigStoreTest(unittest.TestCase):

    def _test_config_store(self, config_store: ConfigStore):
        self.assertEqual({}, config_store.read())
        self.assertIsNot(config_store.read(), config_store.read())
        config = config_store.read()
        config['bibo'] = 42
        config_store.write(config)
        config = config_store.read()
        self.assertEqual(42, config.get('bibo'))

    def test_mem_config_store(self):
        self._test_config_store(MemConfigStore())

    def test_json_config_store(self):
        file_path = '_config_store.json'
        if os.path.exists(file_path):
            os.remove(file_path)
        self._test_config_store(JsonConfigStore(file_path))
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

