import uuid
from dataclasses import dataclass

from foundation.value_objects import DateFrameDefinition

UserId = uuid.UUID


@dataclass
class AbstractUser:
    id: UserId
    date_frame_definition: DateFrameDefinition
