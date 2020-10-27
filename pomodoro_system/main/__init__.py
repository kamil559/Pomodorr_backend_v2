import os
from dataclasses import dataclass

import injector
from dotenv import load_dotenv
from foundation.interfaces import AppSetupStrategy
from foundation.models import db
from foundation.utils import get_config_file_path
from pomodoros import Pomodoros
from pomodoros_infrastructure import PomodorosInfrastructure


@dataclass
class Application:
    settings: dict
    injector: injector.Injector


class TestingSetupStrategy(AppSetupStrategy):
    def load_settings(self) -> None:
        self.settings_mapping = {
            "database": {
                "provider": os.getenv("DB_PROVIDER"),
                "filename": os.getenv("DB_FILENAME"),  # optional (in case of running sqlite3 DB)
            }
        }

    def setup(self) -> None:
        self.load_settings()


class LocalSetupStrategy(AppSetupStrategy):
    def load_settings(self) -> None:
        self.settings_mapping = {
            "database": {
                "provider": os.getenv("DB_PROVIDER"),
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
            }
        }

    def setup(self) -> None:
        self.load_settings()


class ProductionSetupStrategy(AppSetupStrategy):
    def load_settings(self) -> None:
        raise NotImplementedError

    def setup(self) -> None:
        #  postponed until the production setup comes in
        raise NotImplementedError


def _setup_dependencies() -> injector.Injector:
    return injector.Injector([Pomodoros(), PomodorosInfrastructure()], auto_bind=False)


def load_app_settings(settings: dict) -> dict:
    if settings["testing"]:
        setup = TestingSetupStrategy()
    elif settings["debug"]:
        setup = LocalSetupStrategy()
    else:
        setup = ProductionSetupStrategy()
    setup.setup()
    return setup.settings_mapping


def initialize_application() -> Application:
    load_dotenv(dotenv_path=get_config_file_path("APPLICATION_CONFIG"), override=True)
    load_dotenv(dotenv_path=get_config_file_path("DB_CONFIG"), override=True)
    load_dotenv(dotenv_path=get_config_file_path("SECURITY_CONFIG"), override=True)
    load_dotenv(dotenv_path=get_config_file_path("MAIL_CONFIG"), override=True)

    settings = {
        "testing": bool(int(os.getenv("TESTING", False))),
        "debug": bool(int(os.getenv("DEBUG", False))),
    }

    dependency_injector = _setup_dependencies()

    additional_settings = load_app_settings(settings)
    settings.update(additional_settings)

    if not db.provider:
        db.bind(**settings["database"])

    db.generate_mapping(create_tables=True)

    return Application(settings, dependency_injector)
