import flask_injector
import injector

from authorization.tasks import TaskProtector
from foundation.application.repositories.user import UserRepository
from output_boundaries.tasks import JSONPausePomodoroOutputBoundary
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
        return JSONPausePomodoroOutputBoundary()

    @injector.provider
    @flask_injector.request
    def reactivate_task_output_boundary(self) -> ReactivateTaskOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    @flask_injector.request
    def pin_task_to_project_output_boundary(self) -> PinTaskToProjectOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    def begin_pomodoro_resource_protector(self) -> TaskProtector:
        return TaskProtector()

    @injector.provider
    def pause_resume_pomodoro_resource_protector(self) -> PomodoroProtector:
        return PomodoroProtector()

    @injector.provider
    def user_repository(self) -> UserRepository:
        return SQLUserRepository()
