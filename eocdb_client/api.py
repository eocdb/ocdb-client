import json
import os
import urllib.parse
import urllib.request
from io import IOBase
from typing import Any, Dict, Optional, Callable

from eocdb_client.configstore import ConfigStore, JsonConfigStore

UNDEFINED = object()

Config = Dict[str, Any]

# urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
#         *, cafile=None, capath=None, cadefault=False, context=None)
UrlOpener = Callable[[str, Dict[str, Any]], IOBase]


class _DefaultConfigStore(JsonConfigStore):
    USER_DIR = os.path.expanduser(os.path.join('~', '.eocdb'))
    CONFIG_FILE_NAME = 'eocdb-client.json'
    CONFIG_FILE = os.path.join(USER_DIR, CONFIG_FILE_NAME)

    def __init__(self):
        super().__init__(_DefaultConfigStore.CONFIG_FILE)


class Api:
    VALID_CONFIG_PARAM_NAMES = {'server_url'}

    def __init__(self,
                 config_store: ConfigStore = None,
                 server_url: str = None,
                 url_opener: UrlOpener = None):

        if config_store is None:
            config_store = _DefaultConfigStore()
        self._config_store = config_store

        if url_opener is None:
            url_opener = urllib.request.urlopen
        self._url_opener = url_opener

        self._config = None

        if server_url is not None:
            self.server_url = server_url

    @property
    def config(self) -> Config:
        """ Return a copy of the current API configuration. """
        self._ensure_config_initialized()
        return dict(self._config)

    def get_config_param(self, name: str, default: Any = None) -> Optional[Any]:
        """ Get the value of configuration parameter with given *name*. """
        self._ensure_config_initialized()
        return self._config.get(name, default)

    def set_config_param(self, name: str, value: Optional[Any], write: bool = False):
        """ Set the value of configuration parameter with given *name* to *value*. """
        self._ensure_valid_config_name(name)
        self._ensure_config_initialized()
        self._config[name] = value
        if write:
            self._config_store.write(self._config)

    @property
    def server_url(self) -> Optional[str]:
        """ Get the current value of the server URL. May be None, if not configured yet. """
        return self.get_config_param('server_url', None)

    @server_url.setter
    def server_url(self, server_url: str):
        """ Set the the server URL to *server_url*. """
        if not server_url:
            raise ValueError('"server_url" must be specified')
        self.set_config_param('server_url', server_url)

    def query_measurements(self, query: str, index: int = 0, results: int = 100, format='json'):
        params = urllib.parse.urlencode(dict(query=query, index=index, results=results, format=format))
        url = self._make_url(f'/eocdb/api/measurements?{params}')
        with self._url_opener(url) as fp:
            return json.load(fp)

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

    def _ensure_config_initialized(self):
        if self._config is None:
            config = self._config_store.read()
            for name in config:
                self._ensure_valid_config_name(name)
            self._config = config
