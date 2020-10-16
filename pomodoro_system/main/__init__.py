import os
from dataclasses import dataclass

import dotenv
import injector

from foundation.models import db
from pomodoros import Pomodoros
from pomodoros_infrastructure import PomodorosInfrastructure


@dataclass
class Application:
    settings: dict
    injector: injector.Injector


def _get_config_file_path(config_file_name: str) -> str:
    return os.environ.get("CONFIG_PATH",
                          os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, config_file_name))


def _setup_dependencies(settings: dict) -> injector.Injector:
    return injector.Injector(
        [
            Pomodoros(),
            PomodorosInfrastructure()
        ],
        auto_bind=False
    )


def _generate_db_mappings(settings: dict) -> None:
    db.bind(**settings['database'])
    db.generate_mapping(create_tables=True)


def initialize_application() -> Application:
    config_file_path = _get_config_file_path('.envs/local/application')

    dotenv.load_dotenv(config_file_path)

    settings = {
        'database': {
            'provider': os.environ['DB_PROVIDER'],
            'host': os.environ['POSTGRES_HOST'],
            'port': os.environ['POSTGRES_PORT'],
            'user': os.environ['POSTGRES_USER'],
            'password': os.environ['POSTGRES_PASSWORD'],
            'database': os.environ['POSTGRES_DB']
        },
    }

    dependency_injector = _setup_dependencies(settings)
    _generate_db_mappings(settings)

    return Application(settings, dependency_injector)
