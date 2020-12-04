import flask_injector
import injector
from foundation.application.repositories.user import UserRepository
from foundation.interfaces import MediaStorage
from pomodoros import (
    BeginPomodoroOutputBoundary,
    CompleteTaskOutputBoundary,
    FinishPomodoroOutputBoundary,
    PausePomodoroOutputBoundary,
    PinTaskToProjectOutputBoundary,
    ReactivateTaskOutputBoundary,
    ResumePomodoroOutputBoundary,
)
from web_app.authorization.pomodoros import PomodoroProtector
from web_app.users.repository import SQLUserRepository

from .authorization.projects import ProjectProtector
from .authorization.tasks import TaskProtector
from .authorization.tokens import TokenProtector
from .authorization.users import UserProtector
from .media_storages import LocalMediaStorage
from .output_boundaries.pomodoros import (
    JSONBeginPomodoroPresenter,
    JSONFinishPomodoroPresenter,
    JSONPausePomodoroPresenter,
    JSONResumePomodoroPresenter,
)
from .output_boundaries.tasks import (
    JSONCompleteTaskOutputBoundary,
    JSONPinTaskToProjectPresenter,
    JSONReactivateTaskPresenter,
)
from .users.facade import UserFacade


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

    @injector.provider
    def token_protector(self) -> TokenProtector:
        return TokenProtector()

    @injector.provider
    def user_protector(self) -> UserProtector:
        return UserProtector()

    @injector.provider
    def user_facade(self) -> UserFacade:
        return UserFacade()

    @injector.provider
    def media_storage(self) -> MediaStorage:
        return LocalMediaStorage()
