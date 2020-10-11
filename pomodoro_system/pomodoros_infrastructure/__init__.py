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
        # todo: add concrete repository
        pass

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
