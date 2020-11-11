from abc import ABC, abstractmethod
from typing import List

from foundation.value_objects import UserId
from pomodoros.domain.entities import Project


class GetProjectsByOwnerId(ABC):
    @abstractmethod
    def query(self, owner_id: UserId) -> List[Project]:
        pass
