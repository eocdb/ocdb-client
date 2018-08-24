import json
import os
import urllib.parse
import urllib.request
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Optional

UNDEFINED = object()

Config = Dict[str, Any]


class ConfigStore(metaclass=ABCMeta):
    @abstractmethod
    def read(self) -> Config:
        pass

    @abstractmethod
    def write(self, config: Config):
        pass


class MemConfigStore(ConfigStore):
    def __init__(self):
        self._config = dict()

    def read(self) -> Config:
        return dict(self._config)

    def write(self, config: Config):
        self._config.update(config)


class JsonConfigStore(ConfigStore):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> Config:
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {}

    def write(self, config: Config):
        dir_path = os.path.dirname(self.file_path)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        with open(self.file_path, 'w') as fp:
            json.dump(config, fp, indent=4)


class DefaultConfigStore(JsonConfigStore):
    USER_DIR = os.path.expanduser(os.path.join('~', '.eocdb'))
    CONFIG_FILE_NAME = 'eocdb-client.json'
    CONFIG_FILE = os.path.join(USER_DIR, CONFIG_FILE_NAME)

    def __init__(self):
        super().__init__(DefaultConfigStore.CONFIG_FILE)


class Api:
    VALID_CONFIG_PARAM_NAMES = {'server_url'}

    def __init__(self, config_store: ConfigStore = None, server_url: str = None):
        if config_store is None:
            config_store = MemConfigStore()

        config = config_store.read()
        for name in config:
            self._ensure_valid_config_name(name)
        self._config_store = config_store
        self._config = config
        if server_url is not None:
            self.server_url = server_url

    @property
    def config(self) -> Config:
        return self._config

    @property
    def server_url(self) -> Optional[str]:
        return self.get_config_param('server_url', None)

    @server_url.setter
    def server_url(self, server_url: Optional[str]):
        if server_url is None:
            raise ValueError('"server_url" must not be none')
        self.set_config_param('server_url', server_url)

    def get_config_param(self, name: str, default: Any = None):
        return self._config.get(name, default)

    def set_config_param(self, name: str, value: Any, write: bool = False):
        self._ensure_valid_config_name(name)
        self._config[name] = value
        if write:
            self._config_store.write(self._config)

    def query_measurements(self, expr: str, offset: int = 0, num_results: int = 100):
        params = urllib.parse.urlencode(dict(query=expr, offset=offset, num_results=num_results))
        with urllib.request.urlopen(self._make_url(f'/eocdb/api/measurements?{params}')) as f:
            return json.load(f)

    def add_measurements(self, file: str):
        # TODO: implement me
        pass

    def remove_measurements(self, id: str):
        # TODO: implement me
        pass

    def _make_url(self, path: str):
        url = self.server_url
        if not url:
            raise ValueError('"server_url" is not configured')
        if url.endswith('/'):
            url = url[0: -1]
        if not path.startswith('/'):
            path = '/' + path
        return url + path

    @classmethod
    def _ensure_valid_config_name(cls, name: str):
        if name not in cls.VALID_CONFIG_PARAM_NAMES:
            raise ValueError(f'unknown configuration parameter "{name}"')
