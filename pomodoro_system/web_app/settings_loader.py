import os
from datetime import timedelta

from foundation.interfaces import AppSetupStrategy


class FlaskBaseSettingsLoader(AppSetupStrategy):
    def load_settings(self) -> None:
        self.settings_mapping = {
            "base_settings": {
                "SECURITY_REGISTERABLE": True,
                "SECURITY_SEND_REGISTER_EMAIL": True,
                "SECURITY_CONFIRMABLE": True,
                "SECURITY_CHANGEABLE": True,
                "SECURITY_RECOVERABLE": True,
                "WTF_CSRF_ENABLED": False,
                "SECURITY_LOGIN_WITHOUT_CONFIRMATION": False,
                "SECURITY_CSRF_PROTECT_MECHANISMS": [],
                "SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS": True,
                "WTF_CSRF_CHECK_DEFAULT": False,
                "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
                "JWT_TOKEN_LOCATION": ["headers"],
                "JWT_ACCESS_TOKEN_EXPIRES": timedelta(minutes=360),
                "JWT_REFRESH_TOKEN_EXPIRES": timedelta(days=30),
                "JWT_HEADER_NAME": "Authorization",
                "JWT_HEADER_TYPE": "Bearer",
            }
        }

    def setup(self) -> None:
        self.load_settings()


class FlaskTestingSettingsLoader(AppSetupStrategy):
    def load_settings(self) -> None:
        self.settings_mapping = {
            "security": {
                "SECURITY_TOKEN_AUTHENTICATION_HEADER": os.getenv("SECURITY_TOKEN_AUTHENTICATION_HEADER"),
                "SECURITY_EMAIL_SUBJECT_REGISTER": os.getenv("SECURITY_EMAIL_SUBJECT_REGISTER"),
                "SECURITY_CONFIRM_SALT": os.getenv("SECURITY_CONFIRM_SALT"),
                "SECURITY_RESET_SALT": os.getenv("SECURITY_RESET_SALT"),
                "SECURITY_LOGIN_SALT": os.getenv("SECURITY_LOGIN_SALT"),
                "SECURITY_PASSWORD_SALT": os.getenv("SECURITY_PASSWORD_SALT"),
            },
            "mail": {"MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER")},
        }

    def setup(self) -> None:
        self.load_settings()


class FlaskLocalSettingsLoader(AppSetupStrategy):
    def load_settings(self) -> None:
        self.settings_mapping = {
            "security": {
                "SECURITY_TOKEN_AUTHENTICATION_HEADER": os.getenv("SECURITY_TOKEN_AUTHENTICATION_HEADER"),
                "SECURITY_EMAIL_SUBJECT_REGISTER": os.getenv("SECURITY_EMAIL_SUBJECT_REGISTER"),
                "SECURITY_EMAIL_SENDER": os.getenv("SECURITY_EMAIL_SENDER"),
                "SECURITY_CONFIRM_EMAIL_WITHIN": os.getenv("SECURITY_CONFIRM_EMAIL_WITHIN"),
                "SECURITY_RESET_PASSWORD_WITHIN": os.getenv("SECURITY_RESET_PASSWORD_WITHIN"),
                "SECURITY_CONFIRM_SALT": os.getenv("SECURITY_CONFIRM_SALT"),
                "SECURITY_RESET_SALT": os.getenv("SECURITY_RESET_SALT"),
                "SECURITY_LOGIN_SALT": os.getenv("SECURITY_LOGIN_SALT"),
                "SECURITY_PASSWORD_SALT": os.getenv("SECURITY_PASSWORD_SALT"),
            },
            "mail": {
                "MAIL_SERVER": os.getenv("MAIL_SERVER"),
                "MAIL_PORT": os.getenv("MAIL_PORT"),
                "MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER"),
            },
        }

    def setup(self) -> None:
        self.load_settings()


class FlaskStagingSettingsLoader(AppSetupStrategy):
    def load_settings(self) -> None:
        self.settings_mapping = {
            "security": {
                "SECURITY_TOKEN_AUTHENTICATION_HEADER": os.getenv("SECURITY_TOKEN_AUTHENTICATION_HEADER"),
                "SECURITY_EMAIL_SUBJECT_REGISTER": os.getenv("SECURITY_EMAIL_SUBJECT_REGISTER"),
                "SECURITY_EMAIL_SENDER": os.getenv("SECURITY_EMAIL_SENDER"),
                "SECURITY_CONFIRM_EMAIL_WITHIN": os.getenv("SECURITY_CONFIRM_EMAIL_WITHIN"),
                "SECURITY_RESET_PASSWORD_WITHIN": os.getenv("SECURITY_RESET_PASSWORD_WITHIN"),
                "SECURITY_CONFIRM_SALT": os.getenv("SECURITY_CONFIRM_SALT"),
                "SECURITY_RESET_SALT": os.getenv("SECURITY_RESET_SALT"),
                "SECURITY_LOGIN_SALT": os.getenv("SECURITY_LOGIN_SALT"),
                "SECURITY_PASSWORD_SALT": os.getenv("SECURITY_PASSWORD_SALT"),
            },
            "mail": {
                "MAIL_SERVER": os.getenv("MAIL_SERVER"),
                "MAIL_PORT": os.getenv("MAIL_PORT"),
                "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
                "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD"),
                "MAIL_DEFAULT_SENDER": os.getenv("MAIL_DEFAULT_SENDER"),
                "MAIL_MAX_EMAILS": os.getenv("MAIL_MAX_EMAILS"),
                "MAIL_USE_TLS": bool(int(os.getenv("MAIL_USE_TLS"))),
                "MAIL_USE_SSL": bool(int(os.getenv("MAIL_USE_SSL"))),
                "MAIL_ASCII_ATTACHMENTS": bool(int(os.getenv("MAIL_ASCII_ATTACHMENTS"))),
            },
        }

    def setup(self) -> None:
        self.load_settings()


class FlaskProductionSettingsLoader(FlaskStagingSettingsLoader):
    def load_settings(self) -> None:
        #  Load the same environment variables but from production configuration
        super(FlaskProductionSettingsLoader, self).load_settings()

    def setup(self) -> None:
        self.load_settings()
