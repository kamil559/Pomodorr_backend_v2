from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union

from foundation.value_objects import UserId
from pomodoros.domain.entities import Task
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


class GetTaskListByOwnerId(ABC):
    @abstractmethod
    def query(self, owner_id: UserId, return_full_entity: bool = False, **kwargs) -> List[Union[QueryTaskDto, Task]]:
        pass


class GetRecentTasksByProjectId(ABC):
    @abstractmethod
    def query(self, project_id: ProjectId, return_full_entity: bool = False) -> List[QueryTaskDto]:
        pass
