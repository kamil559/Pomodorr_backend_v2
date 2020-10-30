import os

from foundation.interfaces import AppSetupStrategy


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


class StagingSetupStrategy(AppSetupStrategy):
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


class ProductionSetupStrategy(StagingSetupStrategy):
    def load_settings(self) -> None:
        super(ProductionSetupStrategy, self).load_settings()

    def setup(self) -> None:
        #  Load the same environment variables but from production configuration
        self.load_settings()
