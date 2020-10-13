from typing import Type

from pony.orm import ObjectNotFound

from exceptions import NotFound
from foundation.value_objects import Priority
from pomodoros import ProjectRepository, ProjectId
from pomodoros.domain.entities import Project
from pomodoros_infrastructure.models import ProjectModel


class SQLProjectRepository(ProjectRepository):
    @staticmethod
    def _to_entity(project_model: Type[ProjectModel]) -> Project:
        priority = Priority(project_model.priority_color, project_model.priority_level)
        return Project(project_model.id, project_model.name, priority, project_model.ordering, project_model.owner_id,
                       project_model.created_at, project_model.deleted_at)

    def get(self, project_id: ProjectId) -> Project:
        try:
            pause = ProjectModel[project_id]
        except ObjectNotFound:
            raise NotFound()
        else:
            return self._to_entity(pause)

    @staticmethod
    def _get_for_update(project_id: ProjectId) -> Type[ProjectModel]:
        return ProjectModel.get_for_update(project_id)

    def save(self, project: Project) -> None:
        values_to_update = {
            'name': project.name,
            'priority_color': project.priority.color,
            'priority_level': project.priority.priority_level,
            'ordering': project.ordering,
            'owner_id': project.owner_id,
            'created_at': project.created_at,
            'deleted_at': project.deleted_at
        }

        project = self._get_for_update(project.id)
        project.set(**values_to_update)
