from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from foundation.application.repositories.user import UserRepository
from foundation.value_objects import DateFrameDefinition, T, UserId
from pomodoros.application.queries.pomodoros import GetRecentPomodoros
from pomodoros.application.repositories.pomodoros import PomodoroRepository
from pomodoros.application.repositories.tasks import TaskRepository
from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import FrameType, PomodoroId


@dataclass
class FinishPomodoroInputDto:
    id: PomodoroId
    end_date: datetime
    owner_id: UserId


@dataclass
class FinishPomodoroOutputDto:
    id: PomodoroId
    start_date: datetime
    end_date: datetime
    frame_type: FrameType


class FinishPomodoroOutputBoundary(ABC):
    response: Optional[T]

    @abstractmethod
    def present(self, output_dto: FinishPomodoroOutputDto) -> None:
        pass


class FinishPomodoro:
    def __init__(
        self,
        output_boundary: FinishPomodoroOutputBoundary,
        pomodoro_repository: PomodoroRepository,
        task_repository: TaskRepository,
        user_repository: UserRepository,
        recent_pomodoros_query: GetRecentPomodoros,
    ) -> None:
        self.output_boundary = output_boundary
        self.pomodoro_repository = pomodoro_repository
        self.task_repository = task_repository
        self.user_repository = user_repository
        self.recent_pomodoros_query = recent_pomodoros_query

    def _get_date_frame_definition(self, task: Task, user_id: UserId) -> DateFrameDefinition:
        if task.date_frame_definition is not None:
            return task.date_frame_definition

        task_owner = self.user_repository.get(user_id=user_id)
        return task_owner.date_frame_definition

    def execute(self, input_dto: FinishPomodoroInputDto) -> None:
        pomodoro = self.pomodoro_repository.get(input_dto.id)
        task = self.task_repository.get(pomodoro.task_id)
        date_frame_definition = self._get_date_frame_definition(task, input_dto.owner_id)
        recent_pomodoros = self.recent_pomodoros_query.query(task.id)

        pomodoro.finish(date_frame_definition, task, recent_pomodoros, input_dto.end_date)
        self.pomodoro_repository.save(pomodoro)

        output_dto = FinishPomodoroOutputDto(pomodoro.id, pomodoro.start_date, pomodoro.end_date, pomodoro.frame_type)
        self.output_boundary.present(output_dto)
