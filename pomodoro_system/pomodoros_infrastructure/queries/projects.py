from typing import List, Type

from foundation.value_objects import UserId
from pomodoros.application.queries.projects import GetProjectsByOwnerId
from pomodoros.domain.entities import Project
from pomodoros_infrastructure.models.project import ProjectModel
from pomodoros_infrastructure.repositories.projects import SQLProjectRepository
from web_app.mixins import PaginatedQueryMixin, SortedQueryMixin


class SQLGetProjectsByOwnerId(SortedQueryMixin, PaginatedQueryMixin, GetProjectsByOwnerId):
    @staticmethod
    def _to_entity(orm_project: Type[ProjectModel]) -> Project:
        return SQLProjectRepository.to_domain_entity(orm_project)

    def query(self, owner_id: UserId) -> List[Project]:
        orm_projects = ProjectModel.select(lambda project: not project.is_removed and project.owner.id == owner_id)

        orm_projects = self.get_paginated_query(self.get_sorted_query(orm_projects))

        return list(map(lambda project: self._to_entity(project), orm_projects))
