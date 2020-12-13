import os
import pathlib
import string
import uuid
from typing import Type

from flask import current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from foundation.interfaces import FileProtocol, MediaStorage
from werkzeug.datastructures import FileStorage
from werkzeug.local import LocalProxy
from werkzeug.utils import secure_filename

_current_app = LocalProxy(lambda: current_app)


class LocalMediaStorage(MediaStorage):
    def get_file(self, directory: str, filename: str) -> Type[FileProtocol]:
        return send_from_directory(directory, filename)

    def save_file(self, file: FileProtocol, file_path: str) -> str:
        return self._save_new_file(file, file_path)

    @staticmethod
    def _get_secure_filename(file: FileStorage) -> str:
        return secure_filename(file.filename)

    @staticmethod
    def _get_upload_path(file_path: str) -> str:
        formatters = [parsed_param[1] for parsed_param in string.Formatter().parse(file_path)]
        base_path = _current_app.config.get("UPLOAD_PATH", "")

        if "user_id" in formatters:
            directory = file_path.format(user_id=get_jwt_identity())
        else:
            directory = file_path
        return os.path.join(base_path, directory)

    def _get_upload_safe_filename(self, file: FileStorage) -> str:
        filename = self._get_secure_filename(file)
        return f"{uuid.uuid4().hex}_{filename}"

    @staticmethod
    def _create_dir(path: str) -> None:
        if not os.path.isdir(path):
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def _save_new_file(self, file: FileStorage, file_path: str) -> str:
        safe_filename = self._get_upload_safe_filename(file)
        upload_path = self._get_upload_path(file_path)
        save_path = os.path.join(upload_path, safe_filename)

        try:
            file.save(save_path)
        except FileNotFoundError:
            self._create_dir(upload_path)
            file.save(save_path)
        return safe_filename
