import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pomodoros.application.repositories.tasks import TasksRepository
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
    @abstractmethod
    def present(self, output_dto: CompleteTaskOutputDto) -> None:
        pass


class CompleteTaskStrategy(ABC):
    def __init__(self, tasks_repository: TasksRepository) -> None:
        self.tasks_repository = tasks_repository

    @abstractmethod
    def complete_task(self, task: Task) -> CompleteTaskOutputDto:
        pass


class CompleteOneTimeTaskStrategy(CompleteTaskStrategy):
    def complete_task(self, task: Task) -> CompleteTaskOutputDto:
        task.check_can_perform_actions()

        task.status = TaskStatus.COMPLETED

        self.tasks_repository.save(task)
        output_dto = CompleteTaskOutputDto(id=task.id, status=task.status, new_task_id=None)
        return output_dto


class CompleteRepeatableTaskStrategy(CompleteTaskStrategy):
    def complete_task(self, task: Task) -> CompleteTaskOutputDto:
        task.check_can_perform_actions()

        new_task = self._produce_new_task(old_task=task)

        task.status = TaskStatus.COMPLETED
        self.tasks_repository.save(task)
        self.tasks_repository.save(new_task)
        output_dto = CompleteTaskOutputDto(id=task.id, status=task.status, new_task_id=new_task.id)
        return output_dto

    @staticmethod
    def _produce_new_task(old_task: Task) -> Task:
        new_task = deepcopy(old_task)
        new_task.id = uuid.uuid4()
        new_task.due_date = old_task.next_due_date
        return new_task


class CompleteTask:
    def __init__(self, output_boundary: CompleteTaskOutputBoundary, tasks_repository: TasksRepository) -> None:
        self.output_boundary = output_boundary
        self.tasks_repository = tasks_repository
        self._complete_task_strategy: CompleteTaskStrategy = CompleteOneTimeTaskStrategy(tasks_repository)

    def execute(self, input_dto: CompleteTaskInputDto) -> None:
        task = self.tasks_repository.get(task_id=input_dto.id)

        if not task.renewal_interval:
            self._complete_task_strategy = CompleteRepeatableTaskStrategy(self.tasks_repository)

        output_dto = self._complete_task_strategy.complete_task(task=task)
        self.output_boundary.present(output_dto=output_dto)
