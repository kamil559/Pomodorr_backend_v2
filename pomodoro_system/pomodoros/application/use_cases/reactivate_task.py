from abc import ABC, abstractmethod
from dataclasses import dataclass

from pomodoros.application.queries.tasks import GetTasksByProjectId
from pomodoros.application.repositories.tasks import TaskRepository
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
    def __init__(self, output_boundary: ReactivateTaskOutputBoundary, tasks_repository: TaskRepository,
                 get_tasks_by_pomodoro_id_query: GetTasksByProjectId) -> None:
        self.output_boundary = output_boundary
        self.tasks_repository = tasks_repository
        self.get_tasks_by_pomodoro_id_query = get_tasks_by_pomodoro_id_query

    def execute(self, input_dto: ReactivateTaskInputDto) -> None:
        task = self.tasks_repository.get(input_dto.id)
        task_project_tasks_collection = self.get_tasks_by_pomodoro_id_query.query(task.project_id)

        task.reactivate(task_project_tasks_collection)
        self.tasks_repository.save(task)

        output_dto = ReactivateTaskOutputDto(task.id, task.status)
        self.output_boundary.present(output_dto)
