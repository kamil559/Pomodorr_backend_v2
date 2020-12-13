import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Type

from foundation.value_objects import UserDateFrameDefinition, UserId


@dataclass
class AbstractUser:
    id: UserId
    email: str
    avatar: str
    date_frame_definition: UserDateFrameDefinition


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


class FileProtocol(Protocol):
    def save(self, dst, buffer_size) -> None:
        ...

    def close(self) -> None:
        ...


class MediaStorage(ABC):
    @abstractmethod
    def get_file(self, directory: str, filename: str) -> Type[FileProtocol]:
        pass

    @abstractmethod
    def save_file(self, file: FileProtocol, file_path: str) -> str:
        pass
