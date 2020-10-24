import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from foundation.value_objects import T
from pomodoros.application.queries.pomodoros import GetRecentPomodoros
from pomodoros.application.repositories.pomodoros import PomodoroRepository
from pomodoros.application.repositories.tasks import TaskRepository
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import FrameType, TaskId, PomodoroId


@dataclass
class BeginPomodoroInputDto:
    task_id: TaskId
    start_date: datetime


@dataclass
class BeginPomodoroOutputDto:
    id: PomodoroId
    start_date: datetime
    frame_type: FrameType


class BeginPomodoroOutputBoundary(ABC):
    response: Optional[T]

    @abstractmethod
    def present(self, output_dto: BeginPomodoroOutputDto) -> None:
        pass


class BeginPomodoro:
    def __init__(
            self,
            output_boundary: BeginPomodoroOutputBoundary,
            pomodoros_repository: PomodoroRepository,
            tasks_repository: TaskRepository,
            recent_pomodoros_query: GetRecentPomodoros,
    ) -> None:
        self.output_boundary = output_boundary
        self.pomodoros_repository = pomodoros_repository
        self.tasks_repository = tasks_repository
        self.recent_pomodoros_query = recent_pomodoros_query

    @staticmethod
    def _produce_pomodoro(task_id: TaskId) -> Pomodoro:
        return Pomodoro(id=uuid.uuid4(), task_id=task_id)

    def execute(self, input_dto: BeginPomodoroInputDto) -> None:
        task = self.tasks_repository.get(input_dto.task_id)
        recent_pomodoros = self.recent_pomodoros_query.query(input_dto.task_id)

        new_pomodoro = self._produce_pomodoro(task.id)
        new_pomodoro.begin(task, recent_pomodoros, input_dto.start_date)

        self.pomodoros_repository.save(new_pomodoro, create=True)

        output_dto = BeginPomodoroOutputDto(new_pomodoro.id, new_pomodoro.start_date, new_pomodoro.frame_type)
        self.output_boundary.present(output_dto)
