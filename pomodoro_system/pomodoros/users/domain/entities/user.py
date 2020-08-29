from dataclasses import dataclass
from typing import List

from pomodoros.domain.entities import Project
from user_config.domain.entities.user_config import UserConfig


@dataclass
class AbstractUser:
    projects: List[Project]
    config: UserConfig
