from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Type

from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.domain.entities import Task
from pomodoros.domain.exceptions import TaskAlreadyCompleted
from pomodoros.domain.value_objects import TaskId, TaskStatus


@dataclass
class CompleteTaskInputDto:
    id: TaskId
    completed_at: datetime


@dataclass
class CompleteTaskOutputDto:
    id: TaskId
    status: TaskStatus
    new_task_id: Optional[TaskId]


@dataclass
class CompleteTaskOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: CompleteTaskOutputDto) -> None:
        pass


class CompleteTaskStrategy(ABC):
    @abstractmethod
    def complete_task(self, tasks_repository: TasksRepository, task: Task) -> CompleteTaskOutputDto:
        pass


class CompleteOneTimeTaskStrategy(CompleteTaskStrategy):
    def complete_task(self, tasks_repository: TasksRepository, task: Task) -> CompleteTaskOutputDto:
        task.status = TaskStatus.COMPLETED
        tasks_repository.save(task)

        output_dto = CompleteTaskOutputDto(id=task.id, status=task.status, new_task_id=None)
        return output_dto


class CompleteRepeatableTaskStrategy(CompleteTaskStrategy):
    def complete_task(self, tasks_repository: TasksRepository, task: Task) -> CompleteTaskOutputDto:
        # todo: task needs to be created with updated parameters, or:
        # todo: instead of changing the task's status explicitly, one can implement it with event sourcing
        raise NotImplemented


class CompleteTask:
    complete_task_strategy: Type[CompleteTaskStrategy]

    def __init__(self, output_boundary: CompleteTaskOutputBoundary, tasks_repository: TasksRepository) -> None:
        self.output_boundary = output_boundary
        self.tasks_repository = tasks_repository

    @staticmethod
    def _check_is_task_already_completed(task: Task):
        if task.status == TaskStatus.COMPLETED:
            raise TaskAlreadyCompleted

    def execute(self, input_dto: CompleteTaskInputDto) -> None:
        task = self.tasks_repository.get(task_id=input_dto.id)
        self._check_is_task_already_completed(task=task)

        if task.renewal_interval:
            self.complete_task_strategy = CompleteOneTimeTaskStrategy
        else:
            self.complete_task_strategy = CompleteRepeatableTaskStrategy

        output_dto = self.complete_task_strategy.complete_task(tasks_repository=self.tasks_repository, task=task)
        self.output_boundary.present(output_dto=output_dto)
