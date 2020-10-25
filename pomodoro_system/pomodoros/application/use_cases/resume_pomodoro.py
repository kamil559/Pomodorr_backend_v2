from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from foundation.value_objects import T
from pomodoros.application.repositories.pomodoros import PomodoroRepository
from pomodoros.application.repositories.tasks import TaskRepository
from pomodoros.domain.value_objects import PomodoroId


@dataclass
class ResumePomodoroInputDto:
    pomodoro_id: PomodoroId
    resume_date: datetime


@dataclass
class ResumePomodoroOutputDto:
    pomodoro_id: PomodoroId
    resume_date: datetime


class ResumePomodoroOutputBoundary(ABC):
    response: Optional[T]

    @abstractmethod
    def present(self, output_dto: ResumePomodoroOutputDto) -> None:
        pass


class ResumePomodoro:
    def __init__(
        self,
        output_boundary: ResumePomodoroOutputBoundary,
        pomodoros_repository: PomodoroRepository,
        tasks_repository: TaskRepository,
    ) -> None:
        self.output_boundary = output_boundary
        self.pomodoros_repository = pomodoros_repository
        self.tasks_repository = tasks_repository

    def execute(self, input_dto: ResumePomodoroInputDto) -> None:
        pomodoro = self.pomodoros_repository.get(input_dto.pomodoro_id)
        task = self.tasks_repository.get(pomodoro.task_id)

        pomodoro.resume(task, input_dto.resume_date)
        self.pomodoros_repository.save(pomodoro)

        output_dto = ResumePomodoroOutputDto(pomodoro.id, input_dto.resume_date)
        self.output_boundary.present(output_dto)
