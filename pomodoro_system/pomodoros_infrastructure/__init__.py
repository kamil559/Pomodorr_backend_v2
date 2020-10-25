import injector
from pomodoros import (GetRecentPomodoros, GetTasksByProjectId,
                       PauseRepository, PomodoroRepository, ProjectRepository,
                       TaskRepository)

from .models import (PauseModel, PomodoroModel, ProjectModel, SubTaskModel,
                     TaskModel)
from .queries import SQLGetRecentPomodoros, SQLGetTasksByProjectId
from .repositories import (SQLPauseRepository, SQLPomodoroRepository,
                           SQLProjectRepository, SQLTaskRepository)

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
    def get_tasks_by_project_id_query(self) -> GetTasksByProjectId:
        return SQLGetTasksByProjectId()
