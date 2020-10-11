import injector

from pomodoros import (
    PauseRepository,
    PomodorosRepository,
    ProjectsRepository,
    TasksRepository,
    GetRecentPomodoros,
    GetTasksByPomodoroId
)
from .models import Project, Task, SubTask, Pause, Pomodoro
from .repositories import SQLPausesRepository

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
    def pomodoros_repository(self) -> PomodorosRepository:
        # todo: add concrete repository
        pass

    @injector.provider
    def projects_repository(self) -> ProjectsRepository:
        # todo: add concrete repository
        pass

    @injector.provider
    def tasks_repository(self) -> TasksRepository:
        # todo: add concrete repository
        pass

    @injector.provider
    def recent_pomodoros_query(self) -> GetRecentPomodoros:
        # todo: add concrete repository
        pass

    @injector.provider
    def get_tasks_by_pomodoro_id_query(self) -> GetTasksByPomodoroId:
        # todo: add concrete repository
        pass
