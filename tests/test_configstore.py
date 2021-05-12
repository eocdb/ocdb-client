import unittest
import os
import stat
from ocdb.configstore import ConfigStore, MemConfigStore, JsonConfigStore
from ocdb.const import CONFIG_FILE_MODE, CONFIG_DIR_MODE


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

        dir_path = '_test_config_store'
        file_path = f'{dir_path}/config_store.json'
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(dir_path):
            os.rmdir(dir_path)
        self._test_config_store(JsonConfigStore(file_path))
        self.assertTrue(os.path.exists(file_path))
        mode = stat.S_IMODE(os.lstat(file_path).st_mode)
        self.assertEqual(mode, CONFIG_FILE_MODE)
        mode = stat.S_IMODE(os.lstat(dir_path).st_mode)
        self.assertEqual(mode, CONFIG_DIR_MODE)

        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(dir_path):
            os.rmdir(dir_path)
