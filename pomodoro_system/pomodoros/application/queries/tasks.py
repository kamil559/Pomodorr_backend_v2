from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from foundation.interfaces import Paginator
from pomodoros.domain.value_objects import ProjectId, TaskId, TaskStatus


@dataclass
class QueryTaskDto:
    id: TaskId
    name: str
    status: TaskStatus
    project_id: ProjectId

    @property
    def is_active(self) -> bool:
        return self.status == TaskStatus.ACTIVE


class GetTasksByProjectId(ABC):
    @abstractmethod
    def query(
        self, project_id: ProjectId, paginator: Paginator = None, return_full_entity: bool = False
    ) -> List[QueryTaskDto]:
        pass


class GetRecentTasksByProjectId(ABC):
    @abstractmethod
    def query(
        self, project_id: ProjectId, paginator: Paginator = None, return_full_entity: bool = False
    ) -> List[QueryTaskDto]:
        pass
