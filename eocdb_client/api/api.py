from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Optional, Sequence, Union, List

UNDEFINED = object()

Config = Dict[str, Any]

JsonObj = Union[Dict, List]


class Api(metaclass=ABCMeta):

    # Remote dataset access

    @abstractmethod
    def upload_datasets(self, store_path: str, dataset_files: Sequence[str], doc_files: Sequence[str]) -> JsonObj:
        """Upload the given dataset and doc files and return a validation report for each dataset file."""

    @abstractmethod
    def validate_dataset(self, dataset_file: str) -> JsonObj:
        """Validate the given dataset and return a validation report."""

    @abstractmethod
    def add_dataset(self, dataset_file: str):
        """Add a dataset."""

    @abstractmethod
    def update_dataset(self, dataset_file: str):
        """Update a dataset."""

    @abstractmethod
    def delete_dataset(self, dataset_file: str):
        """Delete a dataset."""

    @abstractmethod
    def find_datasets(self,
                      expr: str = None,
                      offset: int = 1,
                      count: int = 1000) -> JsonObj:
        """Find datasets."""

    @abstractmethod
    def get_dataset(self, dataset_id: str) -> JsonObj:
        """Get dataset by ID."""

    @abstractmethod
    def get_dataset_by_name(self, dataset_path: str) -> JsonObj:
        """Get dataset by path and name."""

    @abstractmethod
    def list_datasets_in_path(self, dataset_path: str) -> JsonObj:
        """List datasets in path."""

    # Submission Management

    @abstractmethod
    def get_submission(self, **kwargs) -> JsonObj:
        """Get submission"""

    @abstractmethod
    def get_submissions_for_user(self, **kwargs) -> JsonObj:
        """Get submissions for user"""

    @abstractmethod
    def get_submissions(self, **kwargs) -> JsonObj:
        """Get all submissions"""

    @abstractmethod
    def delete_submission(self, **kwargs) -> JsonObj:
        """Delete submission"""

    @abstractmethod
    def get_submission_files_for_submission(self, **kwargs) -> JsonObj:
        """Get submission files for a submission"""

    @abstractmethod
    def get_submission_file(self, **kwargs) -> JsonObj:
        """Get submission file by submission id and index"""

    @abstractmethod
    def upload_submission_file(self, **kwargs) -> JsonObj:
        """Re-upload a single suibmission file"""

    @abstractmethod
    def delete_submission_file(self, **kwargs) -> JsonObj:
        """Delete s submission file by sbmission Id and index"""

    # User management

    @abstractmethod
    def add_user(self) -> JsonObj:
        """Add a new user"""

    @abstractmethod
    def delete_user(self) -> JsonObj:
        """Delete existing user"""

    @abstractmethod
    def update_user(self) -> JsonObj:
        """Update user Info"""

    @abstractmethod
    def get_user(self) -> JsonObj:
        """Get user info by user ID"""

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
