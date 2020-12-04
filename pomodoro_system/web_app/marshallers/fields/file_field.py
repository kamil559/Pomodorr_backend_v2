import imghdr
import os
import typing

from flask import current_app
from foundation.i18n import N_
from marshmallow import ValidationError, fields
from web_app.utils import get_file_url
from werkzeug.datastructures import FileStorage
from werkzeug.local import LocalProxy
from werkzeug.routing import BuildError
from werkzeug.utils import secure_filename

_current_app = LocalProxy(lambda: current_app)


class FileField(fields.Raw):
    def __init__(
        self, retrieve_file_endpoint: str, allowed_extensions: typing.List[typing.Text] = None, *args, **kwargs
    ) -> None:
        self.retrieve_file_endpoint = retrieve_file_endpoint
        self.allowed_extensions = allowed_extensions
        super(FileField, self).__init__(*args, **kwargs)

    def _serialize(self, value: typing.Any, attr: str, obj: typing.Any, **kwargs) -> str:
        if not isinstance(value, str):
            value = self._get_filename(value)

        try:
            file_url = get_file_url(self.retrieve_file_endpoint, value)
        except BuildError:
            return None
        else:
            return file_url

    @staticmethod
    def _get_filename(file: FileStorage) -> str:
        return secure_filename(file.filename)

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1]

    @property
    def available_extensions(self) -> typing.Set[str]:
        return (
            set(self.allowed_extensions)
            if self.allowed_extensions
            else set(_current_app.config.get("ALLOWED_EXTENSIONS", [])) or set()
        )

    def _has_valid_extension(self, filename: str) -> bool:
        try:
            file_extension = self._get_file_extension(filename)
        except IndexError:
            return False
        else:
            return file_extension in self.available_extensions

    def _is_valid_content(self, stream: FileStorage) -> bool:
        header = stream.read()
        stream.seek(0)
        file_format = imghdr.what(None, header)
        file_extension = f".{file_format if file_format != 'jpeg' else 'jpg'}"

        if not file_format:
            return False
        return file_extension in self.available_extensions

    def _validate(self, value: FileStorage) -> None:
        filename = self._get_filename(value)

        if not filename:
            if self.required:
                raise ValidationError(N_(self.default_error_messages["required"]))
        elif filename and (not self._has_valid_extension(filename) or not self._is_valid_content(value.stream)):
            raise ValidationError(N_("Uploaded file's extension is invalid"))
