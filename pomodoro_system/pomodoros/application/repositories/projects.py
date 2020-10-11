from abc import ABC, abstractmethod

from pomodoros.domain.entities import Project


class ProjectsRepository(ABC):
    @abstractmethod
    def get(self, project_id) -> Project:
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        pass
