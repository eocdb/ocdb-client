import urllib.error
from io import StringIO
from typing import Dict


def new_url_opener_mock(url_to_result_spec: Dict[str, str]):
    class UrlOpener:
        def __init__(self, url: str, **kwargs):
            self.url = url
            self.kwargs = kwargs

        def __enter__(self):
            response = url_to_result_spec.get(self.url, None)
            if response is None:
                raise urllib.error.HTTPError(self.url, 400, f'Resource not found: {self.url}', None, None)
            return StringIO(response)

        def __exit__(self, *args):
            print(args)
            pass

    return UrlOpener
