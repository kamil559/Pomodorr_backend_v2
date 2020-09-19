from dataclasses import dataclass
from typing import List

from foundation.value_objects.user_config import UserConfig
from pomodoros.domain.entities import Project


@dataclass
class AbstractUser:
    projects: List[Project]
    config: UserConfig
