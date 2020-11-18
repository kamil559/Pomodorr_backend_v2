import injector
from pomodoros import (
    GetRecentPomodoros,
    GetTaskListByOwnerId,
    PauseRepository,
    PomodoroRepository,
    ProjectRepository,
    TaskRepository,
)
from pomodoros.application.queries.projects import GetProjectsByOwnerId
from pomodoros.application.queries.tasks import GetRecentTasksByProjectId

from .models import PauseModel, PomodoroModel, ProjectModel, SubTaskModel, TaskModel
from .queries import SQLGetRecentPomodoros, SQLGetRecentTasksByProjectId, SQLGetTaskListByOwnerId
from .queries.projects import SQLGetProjectsByOwnerId
from .repositories import SQLPauseRepository, SQLPomodoroRepository, SQLProjectRepository, SQLTaskRepository

__all__ = [
    # injected module
    "PomodorosInfrastructure",
    # orm models
    "ProjectModel",
    "TaskModel",
    "SubTaskModel",
    "PauseModel",
    "PomodoroModel",
]


class PomodorosInfrastructure(injector.Module):
    @injector.provider
    def pauses_repository(self) -> PauseRepository:
        return SQLPauseRepository()

    @injector.provider
    def pomodoros_repository(self) -> PomodoroRepository:
        return SQLPomodoroRepository()

    @injector.provider
    def projects_repository(self) -> ProjectRepository:
        return SQLProjectRepository()

    @injector.provider
    def tasks_repository(self) -> TaskRepository:
        return SQLTaskRepository()

    @injector.provider
    def recent_pomodoros_query(self) -> GetRecentPomodoros:
        return SQLGetRecentPomodoros()

    @injector.provider
    def get_tasks_by_project_id_query(self) -> GetTaskListByOwnerId:
        return SQLGetTaskListByOwnerId()

    @injector.provider
    def get_recent_tasks_by_project_id_query(self) -> GetRecentTasksByProjectId:
        return SQLGetRecentTasksByProjectId()

    @injector.provider
    def get_projects_by_owner_id_query(self) -> GetProjectsByOwnerId:
        return SQLGetProjectsByOwnerId()
