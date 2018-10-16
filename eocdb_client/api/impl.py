import os
import urllib.parse
import urllib.request
from io import IOBase
from typing import Any, Dict, Optional, Callable

from .api import Api, Config
from .mpf import MultiPartForm
from ..configstore import ConfigStore, JsonConfigStore
from ..version import NAME, VERSION, DESCRIPTION

USER_AGENT = f"{NAME} / {VERSION} {DESCRIPTION}"

# urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
#         *, cafile=None, capath=None, cadefault=False, context=None)
UrlOpener = Callable[[str, Dict[str, Any]], IOBase]


def new_api(config_store: ConfigStore = None, server_url: str = None) -> Api:
    """Create a new API instance."""
    return _ApiImpl(config_store=config_store, server_url=server_url)


class _DefaultConfigStore(JsonConfigStore):
    USER_DIR = os.path.expanduser(os.path.join('~', '.eocdb'))
    CONFIG_FILE_NAME = 'eocdb-client.json'
    CONFIG_FILE = os.path.join(USER_DIR, CONFIG_FILE_NAME)

    def __init__(self):
        super().__init__(_DefaultConfigStore.CONFIG_FILE)


class _ApiImpl(Api):
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

    # Remote dataset access

    def upload_datasets(self,
                        archive_file: str,
                        affil: str = None,
                        project: str = None,
                        cruise: str = None):
        with open(archive_file, "rb") as zip_stream:
            form = MultiPartForm()
            form.add_field('affil', affil or "no_affil")
            form.add_field('project', project or "no_project")
            form.add_field('cruise', cruise or "no_cruise")
            form.add_file('archive_file', os.path.basename(archive_file), zip_stream)
            data = bytes(form)
            request = self._make_request('/eocdb/api/v0.1.0-dev.1/store/upload', data=data, method=form.method)
            request.add_header('Content-type', form.content_type)
            request.add_header('Content-length', len(data))
            with self._url_opener(request) as fp:
                return fp.read()

    def validate_datasets(self, dataset_file: str):
        with open(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request(f'/eocdb/api/v0.1.0-dev.1/datasets/validate',
                                     method="POST",
                                     data=dataset_json)
        with self._url_opener(request) as fp:
            return fp.read()

    def add_dataset(self, dataset_file: str):
        with open(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request(f'/eocdb/api/v0.1.0-dev.1/datasets',
                                     method="PUT",
                                     data=dataset_json)
        with self._url_opener(request) as fp:
            return fp.read()

    def update_dataset(self, dataset_file: str):
        with self._url_opener(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request(f'/eocdb/api/v0.1.0-dev.1/datasets',
                                     method="POST",
                                     data=dataset_json)
        with self._url_opener(request) as fp:
            return fp.read()

    def delete_dataset(self, dataset_id: str) -> str:
        request = self._make_request(f'/eocdb/api/v0.1.0-dev.1/datasets/{dataset_id}', method="DELETE")
        with self._url_opener(request) as fp:
            return fp.read()

    def get_dataset(self, dataset_id: str) -> str:
        request = self._make_request(f'/eocdb/api/v0.1.0-dev.1/datasets/{dataset_id}', method="GET")
        with self._url_opener(request) as fp:
            return fp.read()

    def find_datasets(self, expr: str, offset: int = 1, count: int = 1000) -> str:
        params = urllib.parse.urlencode(dict(expr=expr, offset=offset, results=count))
        request = self._make_request(f'/eocdb/api/v0.1.0-dev.1/datasets?{params}', method="GET")
        with self._url_opener(request) as fp:
            return fp.read()

    # Local configuration access

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

    # Implementation helpers

    def _make_request(self, path: str, method=None, data=None, headers=None) -> urllib.request.Request:
        url = self._make_url(path)
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        request.add_header("User-Agent", USER_AGENT)
        return urllib.request.Request(url, data=data, headers=headers, method=method)

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
