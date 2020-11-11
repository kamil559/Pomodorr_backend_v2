from typing import List, Type

from foundation.utils import with_tzinfo
from foundation.value_objects import Priority, PriorityLevel, UserId
from pomodoros.application.queries.projects import GetProjectsByOwnerId
from pomodoros.domain.entities import Project
from pomodoros_infrastructure import ProjectModel
from web_app.mixins import PaginatedQueryMixin, SortedQueryMixin


class SQLGetProjectsByOwnerId(SortedQueryMixin, PaginatedQueryMixin, GetProjectsByOwnerId):
    @staticmethod
    def _to_entity(project_model: Type[ProjectModel]) -> Project:
        priority = Priority(
            color=project_model.priority_color, priority_level=PriorityLevel(project_model.priority_level)
        )

        return Project(
            id=project_model.id,
            name=project_model.name,
            priority=priority,
            ordering=project_model.ordering,
            owner_id=project_model.owner_id,
            created_at=with_tzinfo(project_model.created_at),
            deleted_at=with_tzinfo(project_model.deleted_at),
        )

    def query(self, owner_id: UserId) -> List[Project]:
        projects = ProjectModel.select(lambda project: not project.is_removed and project.owner_id == owner_id)

        projects = self.get_paginated_query(self.get_sorted_query(projects))

        return list(map(lambda project: self._to_entity(project), projects))
