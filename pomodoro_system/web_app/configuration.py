import flask_injector
import injector

from output_boundaries.pomodoros import JSONBeginPomodoroPresenter, JSONPausePomodoroPresenter
from pomodoros import (
    BeginPomodoroOutputBoundary,
    PausePomodoroOutputBoundary,
    ResumePomodoroOutputBoundary,
    FinishPomodoroOutputBoundary,
    CompleteTaskOutputBoundary,
    ReactivateTaskOutputBoundary,
    PinTaskToProjectOutputBoundary
)


class PomodorosWebb(injector.Module):
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
        # todo: add concrete output boundary
        pass

    @injector.provider
    @flask_injector.request
    def finish_pomodoro_output_boundary(self) -> FinishPomodoroOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    @flask_injector.request
    def complete_task_output_boundary(self) -> CompleteTaskOutputBoundary:
        # todo: add concrete output boundary
        pass

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
