import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from foundation.value_objects import T
from pomodoros.application.repositories.tasks import TaskRepository
from pomodoros.domain.entities import Task
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


class CompleteTaskOutputBoundary(ABC):
    response: Optional[T]

    @abstractmethod
    def present(self, output_dto: CompleteTaskOutputDto) -> None:
        pass


class CompleteTaskStrategy(ABC):
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    @abstractmethod
    def complete_task(self, task: Task) -> CompleteTaskOutputDto:
        pass


class CompleteOneTimeTaskStrategy(CompleteTaskStrategy):
    def complete_task(self, task: Task) -> CompleteTaskOutputDto:
        task.complete()
        self.task_repository.save(task)

        output_dto = CompleteTaskOutputDto(id=task.id, status=task.status, new_task_id=None)
        return output_dto


class CompleteRepeatableTaskStrategy(CompleteTaskStrategy):
    def complete_task(self, task: Task) -> CompleteTaskOutputDto:
        new_task = self._produce_task_for_next_due_date(old_task=task)
        task.complete()

        self.task_repository.save(task)
        self.task_repository.save(new_task, create=True)

        output_dto = CompleteTaskOutputDto(id=task.id, status=task.status, new_task_id=new_task.id)
        return output_dto

    @staticmethod
    def _produce_task_for_next_due_date(old_task: Task) -> Task:
        new_task = deepcopy(old_task)
        new_task.id = uuid.uuid4()
        new_task.due_date = old_task.next_due_date
        return new_task


class CompleteTask:
    def __init__(self, output_boundary: CompleteTaskOutputBoundary, task_repository: TaskRepository) -> None:
        self.output_boundary = output_boundary
        self.task_repository = task_repository
        self._complete_task_strategy: CompleteTaskStrategy = CompleteOneTimeTaskStrategy(task_repository)

    def execute(self, input_dto: CompleteTaskInputDto) -> None:
        task = self.task_repository.get(input_dto.id)

        if task.is_repeatable:
            self._complete_task_strategy = CompleteRepeatableTaskStrategy(self.task_repository)

        output_dto = self._complete_task_strategy.complete_task(task)
        self.output_boundary.present(output_dto)
