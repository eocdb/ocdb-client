import json
import os
import shutil
import urllib.parse
import urllib.request
import zipfile
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
    return OCDBApi(config_store=config_store, server_url=server_url)


class _DefaultConfigStore(JsonConfigStore):

    def __init__(self):
        super().__init__(DEFAULT_CONFIG_FILE)


class OCDBApi(Api):

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

    def upload_submission(self, store_path: str, dataset_files: Sequence[str], doc_files: Sequence[str], path: str,
                          submission_id: str, publication_date: str, allow_publication: bool) -> JsonObj:

        form = MultiPartForm()
        form.add_field('path', path)
        form.add_field('submissionid', submission_id)
        form.add_field('publicationdate', publication_date)
        form.add_field('allowpublication', str(allow_publication))
        form.add_field('userid', str(1))

        for dataset_file in dataset_files:
            form.add_file(f'datasetfiles', os.path.basename(dataset_file), dataset_file, mime_type="text/plain")
        for doc_file in doc_files:
            form.add_file(f'docfiles', os.path.basename(doc_file), doc_file)

        # print(str(form))
        data = bytes(form)

        request = self._make_request('/store/upload/submission', data=data, method=form.method)
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

    def delete_datasets_by_submission(self, submission_id: str):
        request = self._make_request(f'/datasets/submission/{submission_id}', method="DELETE")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def get_datasets_by_submission(self, submission_id: str):
        request = self._make_request(f'/datasets/submission/{submission_id}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

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

    def get_submission(self, submission_id: str) -> JsonObj:
        request = self._make_request(f'/store/upload/submission/{submission_id}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def get_submissions_for_user(self, user_id: int) -> JsonObj:
        request = self._make_request(f'/store/upload/user/{str(user_id)}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def update_submission_status(self, submission_id: str, status: str) -> JsonObj:
        data = {'status': status, 'publication_date': '2020-01-01'}
        data = json.dumps(data).encode('utf-8')

        request = self._make_request(f'/store/status/submission/{submission_id}', data=data, method="PUT")
        request.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def delete_submission(self, submission_id: str) -> JsonObj:
        request = self._make_request(f'/store/upload/submission/{submission_id}', method="DELETE")

        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def download_submission_file(self, submission_id: str, index: int, out_fn: Optional[str]) -> str:
        request = self._make_request(f'/store/download/submissionfile/{submission_id}/{index}', method="GET")

        if not out_fn:
            out_fn = 'download.zip'

        with urllib.request.urlopen(request) as response, open(out_fn, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            out_file.close()
            with zipfile.ZipFile(out_fn) as zf:
                zf.extractall()
        return f'{submission_id}/{index} downloaded to {out_fn}'

    def get_submission_file(self, submission_id: str, index: int) -> JsonObj:
        request = self._make_request(f'/store/upload/submissionfile/{submission_id}/{index}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def delete_submission_file(self, **kwargs) -> JsonObj:
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        params = urllib.parse.urlencode(kwargs)
        request = self._make_request(f'/submission?{params}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def upload_submission_file(self, submission_id: str, index: int, dataset_files: Sequence[str],
                               doc_files: Sequence[str]) -> JsonObj:
        form = MultiPartForm()

        for dataset_file in dataset_files:
            form.add_file(f'datasetfiles', os.path.basename(dataset_file), dataset_file, mime_type="text/plain")
        for doc_file in doc_files:
            form.add_file(f'docfiles', os.path.basename(doc_file), doc_file)

        data = bytes(form)

        request = self._make_request(f'/store/upload/submissionfile/{submission_id}/{index}', data=data, method="PUT")
        request.add_header('Content-type', form.content_type)
        request.add_header('Content-length', len(data))

        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def add_user(self, username: str, password: str, first_name: str, last_name: str, email: str, phone: str,
                 roles: Sequence[str]) -> JsonObj:
        data = {
            'name': username,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'email': email,
            'phone': phone,
            'roles': roles
        }
        data = json.dumps(data).encode('utf-8')

        request = self._make_request(f'/users', data=data, method="POST")
        request.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def delete_user(self, name: str) -> JsonObj:
        request = self._make_request(f'/users/{name}', method="DELETE")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def update_user(self, name: str, key: str, value: str) -> JsonObj:
        user = self.get_user(name)

        user[key] = value
        print(user)

        data = json.dumps(user).encode('utf-8')
        request = self._make_request(f'/users/{name}', data=data, method="PUT")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def get_user(self, name: str) -> JsonObj:
        request = self._make_request(f'/users/{name}', method="GET")
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def login_user(self, username: str, password: str) -> JsonObj:
        data = {'username': username, 'password': password}
        data = json.dumps(data).encode('utf-8')

        request = self._make_request(f'/users/login', data=data, method="POST")
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
