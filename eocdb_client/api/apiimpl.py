import json
import os
import urllib.parse
import urllib.request
from typing import Any, Optional, Sequence

from .api import Api, Config, JsonObj
from .mpf import MultiPartForm
from ..configstore import ConfigStore, JsonConfigStore
from ..version import NAME, VERSION, DESCRIPTION

USER_AGENT = f"{NAME} / {VERSION} {DESCRIPTION}"

API_PATH_PREFIX = "/eocdb/api/v0.1.0"

USER_DIR = os.path.expanduser(os.path.join('~', '.eocdb'))
DEFAULT_CONFIG_FILE_NAME = 'eocdb-client.json'
DEFAULT_CONFIG_FILE = os.path.join(USER_DIR, DEFAULT_CONFIG_FILE_NAME)

VALID_CONFIG_PARAM_NAMES = {'server_url'}


def new_api(config_store: ConfigStore = None, server_url: str = None) -> Api:
    """Factory that creates a new API instance."""
    return ApiImpl(config_store=config_store, server_url=server_url)


class _DefaultConfigStore(JsonConfigStore):

    def __init__(self):
        super().__init__(DEFAULT_CONFIG_FILE)


class ApiImpl(Api):

    def __init__(self,
                 config_store: ConfigStore = None,
                 server_url: str = None):
        if config_store is None:
            config_store = _DefaultConfigStore()
        self._config_store = config_store
        self._config = None
        if server_url is not None:
            self.server_url = server_url

    # Remote dataset access

    def upload_datasets(self, store_path: str, dataset_files: Sequence[str], doc_files: Sequence[str]) -> JsonObj:

        form = MultiPartForm()
        form.add_field('path', store_path)

        for dataset_file in dataset_files:
            form.add_file(f'dataset_files', os.path.basename(dataset_file), dataset_file, mime_type="text/plain")
        for doc_file in doc_files:
            form.add_file(f'doc_files', os.path.basename(doc_file), doc_file)

        # print(str(form))
        data = bytes(form)

        request = self._make_request('/store/upload', data=data, method=form.method)
        request.add_header('Content-type', form.content_type)
        request.add_header('Content-length', len(data))
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def validate_dataset(self, dataset_file: str) -> JsonObj:
        with open(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request('/datasets/validate', method="POST", data=dataset_json.encode("utf-8"))
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def add_dataset(self, dataset_file: str):
        with open(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request('/datasets', method="PUT", data=dataset_json.encode("utf-8"))
        with urllib.request.urlopen(request) as response:
            return response.read()

    def update_dataset(self, dataset_file: str):
        with open(dataset_file) as fp:
            dataset_json = fp.read()
        request = self._make_request(f'/datasets', method="POST", data=dataset_json.encode("utf-8"))
        with urllib.request.urlopen(request) as response:
            return response.read()

    def delete_dataset(self, dataset_id: str):
        request = self._make_request(f'/datasets/{dataset_id}', method="DELETE")
        with urllib.request.urlopen(request) as response:
            return response.read()

    def get_dataset(self, dataset_id: str) -> JsonObj:
        request = self._make_request(f'/datasets/{dataset_id}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def get_dataset_by_name(self, dataset_path: str) -> JsonObj:
        path_components = _split_dataset_path(dataset_path)
        if len(path_components) < 4:
            raise ValueError("Invalid dataset path, "
                             f"must have format affil/project/cruise/name, but was {dataset_path}")
        affil = path_components[0]
        project = path_components[1]
        cruise = path_components[2]
        name = "/".join(path_components[3:])
        request = self._make_request(f'/datasets/{affil}/{project}/{cruise}/{name}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def list_datasets_in_path(self, dataset_path: str) -> JsonObj:
        try:
            affil, project, cruise = _split_dataset_path(dataset_path)
        except ValueError as e:
            raise ValueError(f"Invalid dataset path, "
                             f"must have format affil/project/cruise, but was {dataset_path}") from e
        request = self._make_request(f'/datasets/{affil}/{project}/{cruise}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def find_datasets(self, **kwargs) -> JsonObj:
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        params = urllib.parse.urlencode(kwargs)
        request = self._make_request(f'/datasets?{params}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

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
        if name not in VALID_CONFIG_PARAM_NAMES:
            raise ValueError(f'unknown configuration parameter "{name}"')

    def _ensure_config_initialized(self):
        if self._config is None:
            config = self._config_store.read()
            for name in config:
                self._ensure_valid_config_name(name)
            self._config = config


def _split_dataset_path(dataset_path: str) -> Sequence[str]:
    path_components = dataset_path.split('/')
    for path_component in path_components:
        if path_component.strip() == "":
            raise ValueError(f"Invalid dataset path: {dataset_path}")
    return path_components
