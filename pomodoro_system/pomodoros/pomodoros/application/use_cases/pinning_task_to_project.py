from abc import ABC, abstractmethod
from dataclasses import dataclass

from pomodoros.application.repositories.projects import ProjectsRepository
from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.domain.validations import check_task_name_available_in_project
from pomodoros.domain.value_objects import TaskId, ProjectId


@dataclass
class PinningTaskToProjectInputDto:
    id: TaskId
    name: str
    new_project_id: ProjectId


@dataclass
class PinningTaskToProjectOutputDto:
    id: TaskId
    new_project_id: ProjectId


class PinningTaskToProjectOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: PinningTaskToProjectOutputDto) -> None:
        pass


class PinningTaskToProject:
    def __init__(self, output_boundary: PinningTaskToProjectOutputBoundary, projects_repository: ProjectsRepository,
                 tasks_repository: TasksRepository) -> None:
        self.output_boundary = output_boundary
        self.projects_repository = projects_repository
        self.tasks_repository = tasks_repository

    def execute(self, input_dto: PinningTaskToProjectInputDto) -> None:
        new_project = self.projects_repository.get(project_id=input_dto.new_project_id)
        task = self.tasks_repository.get(task_id=input_dto.id)
        check_task_name_available_in_project(task_name=task.name, project=new_project)

        task.project_id = input_dto.new_project_id
        self.tasks_repository.save(task)

        output_dto = PinningTaskToProjectOutputDto(id=input_dto.id, new_project_id=input_dto.new_project_id)
        self.output_boundary.present(output_dto=output_dto)
