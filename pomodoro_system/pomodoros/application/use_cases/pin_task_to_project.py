from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from foundation.value_objects import T
from pomodoros.application.queries.tasks import GetRecentTasksByProjectId
from pomodoros.application.repositories.tasks import TaskRepository
from pomodoros.domain.value_objects import ProjectId, TaskId


@dataclass
class PinTaskToProjectInputDto:
    id: TaskId
    new_project_id: ProjectId


@dataclass
class PinTaskToProjectOutputDto:
    id: TaskId
    new_project_id: ProjectId


class PinTaskToProjectOutputBoundary(ABC):
    response: Optional[T]

    @abstractmethod
    def present(self, output_dto: PinTaskToProjectOutputDto) -> None:
        pass


class PinTaskToProject:
    def __init__(
        self,
        output_boundary: PinTaskToProjectOutputBoundary,
        tasks_repository: TaskRepository,
        get_recent_tasks_by_pomodoro_id_query: GetRecentTasksByProjectId,
    ) -> None:
        self.output_boundary = output_boundary
        self.tasks_repository = tasks_repository
        self.get_recent_tasks_by_pomodoro_id_query = get_recent_tasks_by_pomodoro_id_query

    def execute(self, input_dto: PinTaskToProjectInputDto) -> None:
        task = self.tasks_repository.get(input_dto.id)
        new_project_tasks = self.get_recent_tasks_by_pomodoro_id_query.query(input_dto.new_project_id)

        task.pin_to_new_project(input_dto.new_project_id, new_project_tasks)
        self.tasks_repository.save(task)

        output_dto = PinTaskToProjectOutputDto(input_dto.id, input_dto.new_project_id)
        self.output_boundary.present(output_dto)
