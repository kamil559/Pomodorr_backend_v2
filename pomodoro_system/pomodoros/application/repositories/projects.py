from abc import ABC, abstractmethod

from pomodoros.domain.entities import Project
from pomodoros.domain.value_objects import ProjectId


class ProjectRepository(ABC):
    @abstractmethod
    def get(self, project_id) -> Project:
        pass

    @abstractmethod
    def save(self, project: Project, create: bool = False) -> None:
        pass

    @abstractmethod
    def delete(self, project_id: ProjectId, permanently: bool = False) -> None:
        pass
