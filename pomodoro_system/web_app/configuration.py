import flask_injector
import injector

from authorization.projects import ProjectProtector
from authorization.tasks import TaskProtector
from foundation.application.repositories.user import UserRepository
from output_boundaries.tasks import (
    JSONCompleteTaskOutputBoundary,
    JSONReactivateTaskPresenter,
    JSONPinTaskToProjectPresenter
)
from pomodoros import (
    BeginPomodoroOutputBoundary,
    PausePomodoroOutputBoundary,
    ResumePomodoroOutputBoundary,
    FinishPomodoroOutputBoundary,
    CompleteTaskOutputBoundary,
    ReactivateTaskOutputBoundary,
    PinTaskToProjectOutputBoundary
)
from web_app.authorization.pomodoros import PomodoroProtector
from web_app.users.repository import SQLUserRepository
from .output_boundaries.pomodoros import (
    JSONBeginPomodoroPresenter,
    JSONPausePomodoroPresenter,
    JSONResumePomodoroPresenter, JSONFinishPomodoroPresenter
)


class PomodorosWeb(injector.Module):
    @injector.provider
    @flask_injector.request
    def begin_pomodoro_output_boundary(self) -> BeginPomodoroOutputBoundary:
        return JSONBeginPomodoroPresenter()

    @injector.provider
    @flask_injector.request
    def pause_pomodoro_output_boundary(self) -> PausePomodoroOutputBoundary:
        return JSONPausePomodoroPresenter()

    @injector.provider
    @flask_injector.request
    def resume_pomodoro_output_boundary(self) -> ResumePomodoroOutputBoundary:
        return JSONResumePomodoroPresenter()

    @injector.provider
    @flask_injector.request
    def finish_pomodoro_output_boundary(self) -> FinishPomodoroOutputBoundary:
        return JSONFinishPomodoroPresenter()

    @injector.provider
    @flask_injector.request
    def complete_task_output_boundary(self) -> CompleteTaskOutputBoundary:
        return JSONCompleteTaskOutputBoundary()

    @injector.provider
    @flask_injector.request
    def reactivate_task_output_boundary(self) -> ReactivateTaskOutputBoundary:
        return JSONReactivateTaskPresenter()

    @injector.provider
    @flask_injector.request
    def pin_task_to_project_output_boundary(self) -> PinTaskToProjectOutputBoundary:
        return JSONPinTaskToProjectPresenter()

    @injector.provider
    def user_repository(self) -> UserRepository:
        return SQLUserRepository()

    @injector.provider
    def task_protector(self) -> TaskProtector:
        return TaskProtector()

    @injector.provider
    def pomodoro_protector(self) -> PomodoroProtector:
        return PomodoroProtector()

    @injector.provider
    def project_protector(self) -> ProjectProtector:
        return ProjectProtector()
