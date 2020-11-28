import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from foundation.value_objects import DateFrameDefinition, UserId


@dataclass
class AbstractUser:
    id: UserId
    date_frame_definition: DateFrameDefinition


@dataclass
class Paginator:
    page: int
    page_size: int = 10

    def is_usable(self) -> bool:
        return (self.page_size is not None and self.page is not None) and self.page > 0


class ResourceProtector(ABC):
    @abstractmethod
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID, abort_if_none: bool = True) -> None:
        pass


class AppSetupStrategy(ABC):
    settings_mapping: dict

    @abstractmethod
    def load_settings(self) -> None:
        pass

    @abstractmethod
    def setup(self) -> None:
        pass
