from abc import ABC, abstractmethod
from dataclasses import dataclass

from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.domain.value_objects import TaskStatus, TaskId


@dataclass
class ReactivateTaskInputDto:
    id: TaskId


@dataclass
class ReactivateTaskOutputDto:
    id: TaskId
    status: TaskStatus


class ReactivateTaskOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: ReactivateTaskOutputDto) -> None:
        pass


class ReactivateTask:
    def __init__(self, output_boundary: ReactivateTaskOutputBoundary, tasks_repository: TasksRepository) -> None:
        self.output_boundary = output_boundary
        self.tasks_repository = tasks_repository

    def execute(self, input_dto: ReactivateTaskInputDto) -> None:
        task = self.tasks_repository.get(task_id=input_dto.id)
        task.reactivate()
        self.tasks_repository.save(task)

        output_dto = ReactivateTaskOutputDto(id=task.id, status=task.status)
        self.output_boundary.present(output_dto=output_dto)
