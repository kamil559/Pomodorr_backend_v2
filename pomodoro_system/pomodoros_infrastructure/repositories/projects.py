from datetime import datetime
from gettext import gettext as _
from typing import Optional, Type

from foundation.exceptions import AlreadyExists, NotFound
from foundation.utils import to_utc, with_tzinfo
from foundation.value_objects import Color, Priority, PriorityLevel
from pomodoros import ProjectId, ProjectRepository
from pomodoros.domain.entities import Project
from pomodoros_infrastructure.models import ProjectModel
from pony.orm import ObjectNotFound


class SQLProjectRepository(ProjectRepository):
    @classmethod
    def to_domain_entity(cls, orm_project: Type[ProjectModel]) -> Project:
        priority = Priority(
            color=Color(hex=orm_project.priority_color), priority_level=PriorityLevel(orm_project.priority_level)
        )
        return Project(
            id=orm_project.id,
            name=orm_project.name,
            priority=priority,
            ordering=orm_project.ordering,
            owner_id=orm_project.owner.id,
            created_at=with_tzinfo(orm_project.created_at),
            deleted_at=with_tzinfo(orm_project.deleted_at),
        )

    @staticmethod
    def _persist_new_orm_project(project_entity: Project) -> None:
        if ProjectModel.exists(owner=project_entity.owner_id, name=project_entity.name):
            raise AlreadyExists({"name": [_("Project already exists.")]})
        else:
            priority = project_entity.priority
            return ProjectModel(
                id=project_entity.id,
                name=project_entity.name,
                priority_color=getattr(priority.color, "hex", None),
                priority_level=getattr(priority.priority_level, "value", None),
                ordering=project_entity.ordering,
                owner=project_entity.owner_id,
                created_at=project_entity.created_at,
                deleted_at=None,
            )

    @staticmethod
    def _get_for_update(project_id: ProjectId) -> Optional[Type[ProjectModel]]:
        return ProjectModel.get_for_update(id=project_id)

    def _update_existing_orm_project(self, project_entity: Project) -> None:
        values_to_update = {
            "name": project_entity.name,
            "priority_color": project_entity.priority.color.hex,
            "priority_level": project_entity.priority.priority_level.value,
            "ordering": project_entity.ordering,
        }
        orm_project = self._get_for_update(project_entity.id)

        if orm_project is not None:
            orm_project.set(**values_to_update)

    def get(self, project_id: ProjectId) -> Project:
        try:
            orm_project = ProjectModel[project_id]
            if orm_project.is_removed:
                raise ObjectNotFound
        except ObjectNotFound:
            raise NotFound(_("Project does not exist"))
        else:
            return self.to_domain_entity(orm_project)

    def save(self, project_entity: Project, create: bool = False) -> None:
        if create:
            self._persist_new_orm_project(project_entity)
        else:
            self._update_existing_orm_project(project_entity)

    def _delete_softly(self, project_id: ProjectId) -> None:
        orm_project = self._get_for_update(project_id)

        if orm_project is not None:
            orm_project.set(deleted_at=to_utc(datetime.now()))

    def delete(self, project_id: ProjectId, permanently: bool = False) -> None:
        if permanently:
            orm_project = ProjectModel.get(id=project_id)
            if orm_project is not None:
                orm_project.delete()
        else:
            self._delete_softly(project_id)
