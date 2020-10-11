import injector

from pomodoros import (
    BeginPomodoroOutputBoundary,
    PausePomodoroOutputBoundary,
    ResumePomodoroOutputBoundary,
    FinishPomodoroOutputBoundary,
    CompleteTaskOutputBoundary,
    ReactivateTaskOutputBoundary,
    PinTaskToProjectOutputBoundary
)


class PomodorosApp(injector.Module):

    @injector.provider
    def begin_pomodoro_output_boundary(self) -> BeginPomodoroOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    def pause_pomodoro_output_boundary(self) -> PausePomodoroOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    def resume_pomodoro_output_boundary(self) -> ResumePomodoroOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    def finish_pomodoro_output_boundary(self) -> FinishPomodoroOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    def complete_task_output_boundary(self) -> CompleteTaskOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    def reactivate_task_output_boundary(self) -> ReactivateTaskOutputBoundary:
        # todo: add concrete output boundary
        pass

    @injector.provider
    def pin_task_to_project_output_boundary(self) -> PinTaskToProjectOutputBoundary:
        # todo: add concrete output boundary
        pass
