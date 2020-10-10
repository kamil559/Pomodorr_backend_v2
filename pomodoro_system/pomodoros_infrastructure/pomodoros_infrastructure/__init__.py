import injector

from pomodoros import (
    PausesRepository,
    PomodorosRepository,
    ProjectsRepository,
    TasksRepository,
    GetRecentPomodoros,
    GetTasksByPomodoroId
)


class PomodorosInfrastructure(injector.Module):
    @injector.provider
    def pauses_repository(self) -> PausesRepository:
        pass

    @injector.provider
    def pomodoros_repository(self) -> PomodorosRepository:
        pass

    @injector.provider
    def projects_repository(self) -> ProjectsRepository:
        pass

    @injector.provider
    def tasks_repository(self) -> TasksRepository:
        pass

    @injector.provider
    def recent_pomodoros_query(self) -> GetRecentPomodoros:
        pass

    @injector.provider
    def get_tasks_by_pomodoro_id_query(self) -> GetTasksByPomodoroId:
        pass
