import os
import urllib.parse
import urllib.request
from io import IOBase
from typing import Any, Dict, Optional, Callable, Sequence

from .api import Api, Config
from .mpf import MultiPartForm
from ..configstore import ConfigStore, JsonConfigStore
from ..version import NAME, VERSION, DESCRIPTION

USER_AGENT = f"{NAME} / {VERSION} {DESCRIPTION}"

API_PATH_PREFIX = "/eocdb/api/v0.1.0"

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

    def upload_datasets(self, store_path: str, dataset_files: Sequence[str], doc_files: Sequence[str]):

        form = MultiPartForm()
        form.add_field('path', store_path)

        input_streams = []
        for dataset_file in dataset_files:
            input_stream = open(dataset_file, "r")
            form.add_file(f'dataset_files', os.path.basename(dataset_file), input_stream, mimetype="text/plain")
            input_streams.append(input_stream)
        for doc_file in doc_files:
            input_stream = open(doc_file, "rb")
            form.add_file(f'doc_files', os.path.basename(doc_file), input_stream)
            input_streams.append(input_stream)

        # print(str(form))
        data = bytes(form)

        for input_stream in input_streams:
            input_stream.close()

        request = self._make_request('/store/upload', data=data, method=form.method)
        request.add_header('Content-type', form.content_type)
        request.add_header('Content-length', len(data))
        with self._url_opener(request) as fp:
            return fp.read()

    def validate_dataset(self, dataset_file: str):
        with open(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request('/datasets/validate', method="POST", data=dataset_json)
        with self._url_opener(request) as fp:
            return fp.read()

    def add_dataset(self, dataset_file: str):
        with open(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request('/datasets', method="PUT", data=dataset_json)
        with self._url_opener(request) as fp:
            return fp.read()

    def update_dataset(self, dataset_file: str):
        with self._url_opener(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request(f'/datasets', method="POST", data=dataset_json)
        with self._url_opener(request) as fp:
            return fp.read()

    def delete_dataset(self, dataset_id: str) -> str:
        request = self._make_request(f'/datasets/{dataset_id}', method="DELETE")
        with self._url_opener(request) as fp:
            return fp.read()

    def get_dataset(self, dataset_id: str) -> str:
        request = self._make_request(f'/datasets/{dataset_id}', method="GET")
        with self._url_opener(request) as fp:
            return fp.read()

    def get_dataset_by_name(self, dataset_path: str) -> str:
        path_components = dataset_path.split('/')
        try:
            for path_component in path_components:
                if path_component.strip() == "":
                    raise ValueError(f"invalid dataset path: {dataset_path}")
            affil, project, cruise, name = dataset_path.split('/')
        except ValueError as e:
            raise ValueError("invalid dataset path, "
                             f"must have format affil/project/cruise/name, but was {dataset_path}") from e
        request = self._make_request(f'/datasets/{affil}/{project}/{cruise}/{name}', method="GET")
        with self._url_opener(request) as fp:
            return fp.read()

    def get_datasets_in_path(self, dataset_path: str) -> str:
        path_components = dataset_path.split('/')
        try:
            for path_component in path_components:
                if path_component.strip() == "":
                    raise ValueError(f"invalid dataset path: {dataset_path}")
            affil, project, cruise = dataset_path.split('/')
        except ValueError as e:
            raise ValueError(f"invalid dataset path, "
                             f"must have format affil/project/cruise, but was {dataset_path}") from e
        request = self._make_request(f'/datasets/{affil}/{project}/{cruise}', method="GET")
        with self._url_opener(request) as fp:
            return fp.read()

    def find_datasets(self, expr: str, offset: int = 1, count: int = 1000) -> str:
        params = urllib.parse.urlencode(dict(expr=expr, offset=offset, results=count))
        request = self._make_request(f'/datasets?{params}', method="GET")
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
        request = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
        request.add_header("User-Agent", USER_AGENT)
        return request

    def _make_url(self, path: str):
        url = self.server_url
        if not url:
            raise ValueError('"server_url" is not configured')
        if url.endswith('/'):
            url = url[0: -1]
        if not path.startswith('/'):
            path = '/' + path
        return url + API_PATH_PREFIX + path

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
