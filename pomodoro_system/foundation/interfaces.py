import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from foundation.value_objects import UserId, DateFrameDefinition


@dataclass
class AbstractUser:
    id: UserId
    date_frame_definition: DateFrameDefinition


class ResourceProtector(ABC):
    @abstractmethod
    def authorize(self, requester_id: UserId, resource_id: uuid.UUID) -> None:
        pass
