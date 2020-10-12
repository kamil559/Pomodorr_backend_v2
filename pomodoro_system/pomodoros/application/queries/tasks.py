from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from pomodoros.domain.value_objects import TaskId, TaskStatus, ProjectId


@dataclass
class TaskDto:
    id: TaskId
    name: str
    status: TaskStatus
    project_id: ProjectId

    @property
    def is_active(self) -> bool:
        return self.status == TaskStatus.ACTIVE


class GetTasksByProjectId(ABC):
    @abstractmethod
    def query(self, project_id: ProjectId) -> Optional[List[TaskDto]]:
        pass
