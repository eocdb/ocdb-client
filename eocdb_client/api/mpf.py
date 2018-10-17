import io
import mimetypes
import uuid
from typing import BinaryIO, TextIO, Union


class MultiPartForm:
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self._fields = []
        self._files = []
        self._boundary = uuid.uuid4().hex

    @property
    def method(self) -> str:
        return "POST"

    @property
    def content_type(self) -> str:
        return f'multipart/form-data; boundary={self._boundary}'

    def add_field(self, field_name: str, field_value: str):
        """Add a simple field to the form data."""
        self._fields.append((field_name, field_value))

    def add_file(self, field_name: str, file_name: str, file_handle: Union[TextIO, BinaryIO], mimetype: str = None):
        """Add a file to be uploaded."""
        body = file_handle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        self._files.append((field_name, file_name, mimetype, body))

    def _boundary_line(self, final=False) -> bytes:
        if final:
            return b"--" + self._boundary.encode("utf-8") + b"--\r\n"
        return b"--" + self._boundary.encode("utf-8") + b"\r\n"

    @staticmethod
    def _content_disposition_line(disposition_type="form-data", name: str = None, filename=None) -> bytes:
        line = f'Content-Disposition: {disposition_type}; name="{name}"'
        if filename:
            line += f'; filename="{filename}"'
        return (line + "\r\n").encode('utf-8')

    @staticmethod
    def _content_type_line(content_type: str, boundary=None) -> bytes:
        line = f'Content-Type: {content_type}'
        if boundary:
            line += f'; boundary={boundary}'
        return (line + "\r\n").encode('utf-8')

    def __bytes__(self):
        """Return a byte-string representing the form data,
        including attached files.
        """
        buffer = io.BytesIO()

        # Add the form fields
        for field_name, field_value in self._fields:
            buffer.write(self._boundary_line())
            buffer.write(self._content_disposition_line(name=field_name))
            buffer.write(b'\r\n')
            buffer.write(field_value.encode('utf-8'))
            buffer.write(b'\r\n')

        for field_name, file_name, file_content_type, file_body in self._files:
            buffer.write(self._boundary_line())
            buffer.write(self._content_disposition_line(name=field_name, filename=file_name))
            buffer.write(self._content_type_line(content_type=file_content_type))
            buffer.write(b'\r\n')
            buffer.write(file_body if isinstance(file_body, bytes) else file_body.encode("utf-8"))
            buffer.write(b'\r\n')

        # Write final boundary
        buffer.write(self._boundary_line(final=True))
        return buffer.getvalue()

    def __str__(self):
        return "\n".join(bytes(self).decode("utf-8").split("\r\n"))
