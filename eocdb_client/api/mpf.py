import io
import mimetypes
import urllib.request
import uuid
from typing import BinaryIO


class MultiPartForm:
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self._fields = []
        self._files = []
        # Use a large random byte string to separate parts of the MIME data.
        self._boundary = uuid.uuid4().hex.encode('utf-8')

    @property
    def method(self) -> str:
        return "POST"

    @property
    def content_type(self) -> str:
        return 'multipart/form-data; boundary={}'.format(self._boundary.decode('utf-8'))

    def add_field(self, field_name: str, field_value: str):
        """Add a simple field to the form data."""
        self._fields.append((field_name, field_value))

    def add_file(self, field_name: str, file_name: str, file_handle: BinaryIO, mimetype: str = None):
        """Add a file to be uploaded."""
        body = file_handle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        self._files.append((field_name, file_name, mimetype, body))

    @staticmethod
    def _form_data_bytes(field_name: str) -> bytes:
        return f'Content-Disposition: form-data; name="{field_name}"\r\n'.encode('utf-8')

    @staticmethod
    def _attached_file_bytes(field_name: str, file_name: str) -> bytes:
        return f'Content-Disposition: file; name="{field_name}"; filename="{file_name}"\r\n'.encode('utf-8')

    @staticmethod
    def _content_type_bytes(content_type: str) -> bytes:
        return f'Content-Type: {content_type}\r\n'.encode('utf-8')

    def __bytes__(self):
        """Return a byte-string representing the form data,
        including attached files.
        """
        buffer = io.BytesIO()
        boundary = b'--' + self._boundary + b'\r\n'

        # Add the form fields
        for field_name, field_value in self._fields:
            buffer.write(boundary)
            buffer.write(self._form_data_bytes(field_name))
            buffer.write(b'\r\n')
            buffer.write(field_value.encode('utf-8'))
            buffer.write(b'\r\n')

        # Add the files to upload
        for field_name, file_name, file_content_type, file_body in self._files:
            buffer.write(boundary)
            buffer.write(self._attached_file_bytes(field_name, file_name))
            buffer.write(self._content_type_bytes(file_content_type))
            buffer.write(b'\r\n')
            buffer.write(file_body)
            buffer.write(b'\r\n')

        buffer.write(b'--' + self._boundary + b'--\r\n')
        return buffer.getvalue()


if __name__ == '__main__':
    # Create the form with simple fields
    form = MultiPartForm()
    form.add_field('firstname', 'Doug')
    form.add_field('lastname', 'Hellmann')

    # Add a fake file
    form.add_file(
        'biography', 'bio.txt',
        file_handle=io.BytesIO(b'Python developer and blogger.'))

    # Build the request, including the byte-string
    # for the data to be posted.
    data = bytes(form)
    r = urllib.request.Request('http://localhost:8080/', data=data)
    r.add_header(
        'User-agent',
        'PyMOTW (https://pymotw.com/)',
    )
    r.add_header('Content-type', form.get_content_type())
    r.add_header('Content-length', len(data))

    print()
    print('OUTGOING DATA:')
    for name, value in r.header_items():
        print('{}: {}'.format(name, value))
    print()
    print(r.data.decode('utf-8'))

    print()
    print('SERVER RESPONSE:')
    print(urllib.request.urlopen(r).read().decode('utf-8'))
