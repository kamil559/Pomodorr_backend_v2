from dataclasses import dataclass
from typing import List

from pomodoros.domain.entities import Project


@dataclass
class AbstractUser:
    projects: List[Project]
