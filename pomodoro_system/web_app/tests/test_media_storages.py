from unittest.mock import Mock

from flask import Flask
from web_app.media_storages import LocalMediaStorage


class TestLocalMediaStorage:
    def test_save_file(self, app: Flask, jpg_file):
        with app.test_request_context():
            media_storage = LocalMediaStorage()
            jpg_file.save = Mock(return_value=None)
            save_dir = "sample_dir"

            filename = media_storage.save_file(jpg_file, save_dir)
            expected_path = f"pomodoro_system/web_app/media/{save_dir}/{filename}"

            jpg_file.save.assert_called_once_with(expected_path)
