import os
from dataclasses import dataclass

import dotenv
import injector

from pomodoros import Pomodoros
from pomodoros_infrastructure.pomodoros_infrastructure import PomodorosInfrastructure


@dataclass
class Application:
    injector: injector.Injector


def _get_config_file_path(config_file_name: str) -> str:
    return os.environ.get(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, config_file_name))


def _setup_dependencies(settings: dict) -> injector.Injector:
    return injector.Injector([
        Pomodoros(),
        PomodorosInfrastructure()
    ],
        auto_bind=False
    )


def initialize_application() -> Application:
    config_file_path = _get_config_file_path('.envs')

    dotenv.load_dotenv(config_file_path)

    settings = {
        'database': {
            'provider': os.environ['db_provider'],
            'host': os.environ['db_host'],
            'user': os.environ['db_user'],
            'password': os.environ['db_password'],
            'database': os.environ['db_database']
        },
    }

    dependency_injector = _setup_dependencies(settings)

    return Application(dependency_injector)
