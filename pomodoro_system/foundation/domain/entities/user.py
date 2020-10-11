from dataclasses import dataclass

from foundation.value_objects import DateFrameDefinition, UserId


@dataclass
class AbstractUser:
    id: UserId
    date_frame_definition: DateFrameDefinition
