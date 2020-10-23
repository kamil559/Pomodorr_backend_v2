import injector

from foundation.application.repositories.user import UserRepository
from pomodoros.application.queries.pomodoros import GetRecentPomodoros
from pomodoros.application.queries.tasks import GetTasksByProjectId, TaskDto
from pomodoros.application.repositories.pauses import PauseRepository
from pomodoros.application.repositories.pomodoros import PomodoroRepository
from pomodoros.application.repositories.projects import ProjectRepository
from pomodoros.application.repositories.tasks import TaskRepository
from pomodoros.application.use_cases.begin_pomodoro import (
    BeginPomodoroOutputBoundary,
    BeginPomodoro,
    BeginPomodoroInputDto,
    BeginPomodoroOutputDto
)
from pomodoros.application.use_cases.complete_task import (
    CompleteTaskOutputBoundary,
    CompleteTask,
    CompleteTaskInputDto,
    CompleteTaskOutputDto
)
from pomodoros.application.use_cases.finish_pomodoro import (
    FinishPomodoro,
    FinishPomodoroOutputBoundary,
    FinishPomodoroInputDto,
    FinishPomodoroOutputDto
)
from pomodoros.application.use_cases.pause_pomodoro import (
    PausePomodoro,
    PausePomodoroOutputBoundary,
    PausePomodoroInputDto,
    PausePomodoroOutputDto
)
from pomodoros.application.use_cases.pin_task_to_project import (
    PinTaskToProject,
    PinTaskToProjectOutputBoundary,
    PinTaskToProjectInputDto,
    PinTaskToProjectOutputDto
)
from pomodoros.application.use_cases.reactivate_task import (
    ReactivateTaskOutputBoundary,
    ReactivateTask,
    ReactivateTaskInputDto,
    ReactivateTaskOutputDto
)
from pomodoros.application.use_cases.resume_pomodoro import (
    ResumePomodoro,
    ResumePomodoroOutputBoundary,
    ResumePomodoroInputDto,
    ResumePomodoroOutputDto
)
from pomodoros.domain.value_objects import ProjectId, TaskId, SubTaskId, PomodoroId, PauseId

__all__ = [
    # injected module
    'Pomodoros',

    # value objects
    'ProjectId',
    'TaskId',
    'SubTaskId',
    'PomodoroId',
    'PauseId',

    # repositories
    'PauseRepository',
    'PomodoroRepository',
    'ProjectRepository',
    'TaskRepository',

    # use cases
    'BeginPomodoro',
    'PausePomodoro',
    'ResumePomodoro',
    'FinishPomodoro',
    'CompleteTask',
    'ReactivateTask',
    'PinTaskToProject',

    # input dtos
    'BeginPomodoroInputDto',
    'PausePomodoroInputDto',
    'ResumePomodoroInputDto',
    'FinishPomodoroInputDto',
    'CompleteTaskInputDto',
    'ReactivateTaskInputDto',
    'PinTaskToProjectInputDto',

    # output dtos
    'BeginPomodoroOutputDto',
    'PausePomodoroOutputDto',
    'ResumePomodoroOutputDto',
    'FinishPomodoroOutputDto',
    'CompleteTaskOutputDto',
    'ReactivateTaskOutputDto',
    'PinTaskToProjectOutputDto',

    # output boundaries
    'BeginPomodoroOutputBoundary',
    'PausePomodoroOutputBoundary',
    'ResumePomodoroOutputBoundary',
    'FinishPomodoroOutputBoundary',
    'CompleteTaskOutputBoundary',
    'ReactivateTaskOutputBoundary',
    'PinTaskToProjectOutputBoundary',

    # queries
    'GetRecentPomodoros',
    'GetTasksByProjectId',

    # queries dtos
    'TaskDto'
]


class Pomodoros(injector.Module):
    @injector.provider
    def begin_pomodoro_uc(self, output_boundary: BeginPomodoroOutputBoundary,
                          pomodoros_repository: PomodoroRepository,
                          tasks_repository: TaskRepository,
                          recent_pomodoros_query: GetRecentPomodoros) -> BeginPomodoro:
        return BeginPomodoro(output_boundary, pomodoros_repository, tasks_repository, recent_pomodoros_query)

    @injector.provider
    def pause_pomodoro_uc(self, output_boundary: PausePomodoroOutputBoundary, pomodoros_repository: PomodoroRepository,
                          tasks_repository: TaskRepository) -> PausePomodoro:
        return PausePomodoro(output_boundary, pomodoros_repository, tasks_repository)

    @injector.provider
    def resume_pomodoro_uc(self, output_boundary: ResumePomodoroOutputBoundary,
                           pomodoros_repository: PomodoroRepository,
                           tasks_repository: TaskRepository) -> ResumePomodoro:
        return ResumePomodoro(output_boundary, pomodoros_repository, tasks_repository)

    @injector.provider
    def finish_pomodoro_uc(self, output_boundary: FinishPomodoroOutputBoundary,
                           pomodoros_repository: PomodoroRepository, tasks_repository: TaskRepository,
                           users_repository: UserRepository,
                           recent_pomodoros_query: GetRecentPomodoros) -> FinishPomodoro:
        return FinishPomodoro(output_boundary, pomodoros_repository, tasks_repository, users_repository,
                              recent_pomodoros_query)

    @injector.provider
    def complete_task_uc(self, output_boundary: CompleteTaskOutputBoundary,
                         tasks_repository: TaskRepository) -> CompleteTask:
        return CompleteTask(output_boundary, tasks_repository)

    @injector.provider
    def reactivate_task_uc(self, output_boundary: ReactivateTaskOutputBoundary, tasks_repository: TaskRepository,
                           get_tasks_by_pomodoro_id_query: GetTasksByProjectId) -> ReactivateTask:
        return ReactivateTask(output_boundary, tasks_repository, get_tasks_by_pomodoro_id_query)

    @injector.provider
    def pin_task_to_project_provider(self, output_boundary: PinTaskToProjectOutputBoundary,
                                     tasks_repository: TaskRepository,
                                     get_tasks_by_project_id_query: GetTasksByProjectId) -> PinTaskToProject:
        return PinTaskToProject(output_boundary, tasks_repository, get_tasks_by_project_id_query)
