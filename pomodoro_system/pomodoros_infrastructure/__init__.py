import injector

from pomodoros import (
    PauseRepository,
    PomodoroRepository,
    ProjectRepository,
    TaskRepository,
    GetRecentPomodoros,
    GetTasksByPomodoroId
)
from .models import Project, Task, SubTask, Pause, Pomodoro
from .repositories import SQLPausesRepository, SQLPomodoroRepository, SQLProjectRepository, SQLTaskRepository

__all__ = [
    # injected module
    'PomodorosInfrastructure',

    # orm models
    'Project',
    'Task',
    'SubTask',
    'Pause',
    'Pomodoro'
]


class PomodorosInfrastructure(injector.Module):
    @injector.provider
    def pauses_repository(self) -> PauseRepository:
        return SQLPausesRepository()

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
        # todo: add concrete repository
        pass

    @injector.provider
    def get_tasks_by_pomodoro_id_query(self) -> GetTasksByPomodoroId:
        # todo: add concrete repository
        pass
