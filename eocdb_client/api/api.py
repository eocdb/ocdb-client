from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Optional, Sequence, Union, List

UNDEFINED = object()

Config = Dict[str, Any]

JsonObj = Union[Dict, List]


class Api(metaclass=ABCMeta):

    # Remote dataset access

    @abstractmethod
    def upload_datasets(self, store_path: str, dataset_files: Sequence[str], doc_files: Sequence[str]) -> JsonObj:
        pass

    @abstractmethod
    def validate_dataset(self, dataset_file: str) -> JsonObj:
        pass

    @abstractmethod
    def add_dataset(self, dataset_file: str):
        pass

    @abstractmethod
    def update_dataset(self, dataset_file: str):
        pass

    @abstractmethod
    def delete_dataset(self, dataset_file: str):
        pass

    @abstractmethod
    def find_datasets(self, expr: str, offset: int = 1, count: int = 1000) -> JsonObj:
        pass

    @abstractmethod
    def get_dataset(self, dataset_id: str) -> JsonObj:
        pass

    @abstractmethod
    def get_dataset_by_name(self, dataset_path: str) -> JsonObj:
        pass

    @abstractmethod
    def list_datasets_in_path(self, dataset_path: str) -> JsonObj:
        pass

    # Local configuration access

    @property
    @abstractmethod
    def config(self) -> Config:
        """ Return a copy of the current API configuration. """

    @abstractmethod
    def get_config_param(self, name: str, default: Any = None) -> Optional[Any]:
        """ Get the value of configuration parameter with given *name*. """

    @abstractmethod
    def set_config_param(self, name: str, value: Optional[Any], write: bool = False):
        """ Set the value of configuration parameter with given *name* to *value*. """

    @property
    @abstractmethod
    def server_url(self) -> Optional[str]:
        """ Get the current value of the server URL. May be None, if not configured yet. """

    @server_url.setter
    @abstractmethod
    def server_url(self, server_url: str):
        """ Set the the server URL to *server_url*. """
