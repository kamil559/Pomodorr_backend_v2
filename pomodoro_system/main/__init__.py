import os
from dataclasses import dataclass

import injector
from dotenv import load_dotenv
from foundation.models import db
from pomodoros import Pomodoros
from pomodoros_infrastructure import PomodorosInfrastructure


@dataclass
class Application:
    settings: dict
    injector: injector.Injector


def _get_config_file_path(env_name: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.environ.get(env_name)))


def _setup_dependencies(settings: dict) -> injector.Injector:
    return injector.Injector([Pomodoros(), PomodorosInfrastructure()], auto_bind=False)


def _generate_db_mappings(settings: dict) -> None:
    if bool(os.getenv("TESTING")):
        db.bind(
            provider=settings["database"]["provider"],
            filename=settings["database"]["filename"],
        )
    else:
        db.bind(**settings["database"])
    db.generate_mapping(create_tables=True)


def initialize_application() -> Application:
    app_config_file_path = _get_config_file_path("APPLICATION_CONFIG")
    db_config_file_path = _get_config_file_path("DB_CONFIG")
    load_dotenv(dotenv_path=app_config_file_path, override=True)
    load_dotenv(dotenv_path=db_config_file_path, override=True)

    settings = {
        "database": {
            "provider": os.getenv("DB_PROVIDER"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "filename": os.getenv("DB_FILENAME"),  # optional (in case of running sqlite3 DB)
        },
    }

    dependency_injector = _setup_dependencies(settings)
    _generate_db_mappings(settings)

    return Application(settings, dependency_injector)
