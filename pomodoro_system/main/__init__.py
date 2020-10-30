import os
from dataclasses import dataclass

import injector
from dotenv import load_dotenv
from foundation.models import db
from foundation.utils import get_config_file_path
from main.settings_loader import LocalSetupStrategy, ProductionSetupStrategy, StagingSetupStrategy, TestingSetupStrategy
from pomodoros import Pomodoros
from pomodoros_infrastructure import PomodorosInfrastructure


@dataclass
class Application:
    settings: dict
    injector: injector.Injector


def inject_dependencies() -> injector.Injector:
    return injector.Injector([Pomodoros(), PomodorosInfrastructure()], auto_bind=False)


def load_app_settings(settings: dict) -> dict:
    if settings["testing"]:
        setup_strategy = TestingSetupStrategy()
    elif settings["debug"]:
        setup_strategy = LocalSetupStrategy()
    elif settings["debug"]:
        setup_strategy = StagingSetupStrategy()
    else:
        setup_strategy = ProductionSetupStrategy()
    setup_strategy.setup()
    return setup_strategy.settings_mapping


def setup_database(database_settings: dict) -> None:
    if not db.provider:
        db.bind(**database_settings)

    if not db.schema:
        db.generate_mapping(create_tables=True, check_tables=True)


def initialize_application() -> Application:
    load_dotenv(dotenv_path=get_config_file_path("APPLICATION_CONFIG"), override=True)
    load_dotenv(dotenv_path=get_config_file_path("DB_CONFIG"), override=True)
    load_dotenv(dotenv_path=get_config_file_path("SECURITY_CONFIG"), override=True)
    load_dotenv(dotenv_path=get_config_file_path("MAIL_CONFIG"), override=True)

    settings = {
        "testing": bool(int(os.getenv("TESTING", False))),
        "debug": bool(int(os.getenv("DEBUG", False))),
        "staging": bool(int(os.getenv("STAGING", False))),
    }

    dependency_injector = inject_dependencies()

    additional_settings = load_app_settings(settings)
    settings.update(additional_settings)

    setup_database(settings["database"])

    return Application(settings, dependency_injector)
