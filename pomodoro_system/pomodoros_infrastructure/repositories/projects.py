from datetime import datetime
from typing import Type

from foundation.exceptions import AlreadyExists, NotFound
from foundation.utils import to_utc, with_tzinfo
from foundation.value_objects import Priority, PriorityLevel
from pomodoros import ProjectId, ProjectRepository
from pomodoros.domain.entities import Project
from pomodoros_infrastructure.models import ProjectModel
from pony.orm import ObjectNotFound


class SQLProjectRepository(ProjectRepository):
    @staticmethod
    def _to_entity(project_model: Type[ProjectModel]) -> Project:
        priority = Priority(project_model.priority_color, PriorityLevel(project_model.priority_level))
        return Project(
            project_model.id,
            project_model.name,
            priority,
            project_model.ordering,
            project_model.owner_id,
            with_tzinfo(project_model.created_at),
            with_tzinfo(project_model.deleted_at),
        )

    def get(self, project_id: ProjectId) -> Project:
        try:
            project = ProjectModel[project_id]
        except ObjectNotFound:
            raise NotFound()
        else:
            if project.is_removed:
                return None
            return self._to_entity(project)

    @staticmethod
    def _persist_new_project_entity(project):
        if ProjectModel.exists(id=project.id):
            raise AlreadyExists()
        else:
            return ProjectModel(
                id=project.id,
                name=project.name,
                priority_color=getattr(project.priority, "color", None),
                priority_level=getattr(project.priority.priority_level, "value", None),
                ordering=project.ordering,
                owner_id=project.owner_id,
                created_at=project.created_at,
                deleted_at=None,
            )

    @staticmethod
    def _get_for_update(project_id: ProjectId) -> Type[ProjectModel]:
        return ProjectModel.get_for_update(id=project_id)

    def save(self, project: Project, create: bool = False) -> None:
        if create:
            self._persist_new_project_entity(project)
        else:
            values_to_update = {
                "name": project.name,
                "priority_color": project.priority.color,
                "priority_level": project.priority.priority_level.value,
                "ordering": project.ordering,
                "deleted_at": to_utc(project.deleted_at),
            }

            project = self._get_for_update(project.id)
            project.set(**values_to_update)

    def delete(self, project_id: ProjectId, permanently: bool = False) -> None:
        if permanently:
            ProjectModel[project_id].delete()
        else:
            ProjectModel[project_id].set(deleted_at=to_utc(datetime.now()))
