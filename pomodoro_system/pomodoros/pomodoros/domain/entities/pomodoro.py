from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, List

from pomodoros.domain.entities import DateFrame, Task
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.value_objects import FrameType
from user_config.domain.entities.user_config import UserConfig


@dataclass
class Pomodoro(DateFrame):
    task: Task
    frame_type = FrameType.TYPE_POMODORO
    contained_pauses: Optional[List[Pause]]

    @property
    def maximal_duration(self) -> timedelta:
        date_frame_owner = self.task.project.owner
        user_config = date_frame_owner.config
        return self._normalized_length(user_config=user_config)

    def _normalized_length(self, user_config: UserConfig):
        if self.task.pomodoro_length is not None:
            return self.task.pomodoro_length
        return user_config.pomodoro_length
