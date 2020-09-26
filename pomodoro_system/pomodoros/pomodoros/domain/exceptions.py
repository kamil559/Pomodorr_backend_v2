class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidProjectOwner(ValidationError):
    pass


class TaskNameNotAvailableInNewProject(ValidationError):
    pass


class TaskForDueDateAlreadyExists(ValidationError):
    pass


class TaskAlreadyActive(ValidationError):
    pass


class TaskAlreadyCompleted(ValidationError):
    pass


class SubTaskNotAvailableInTask(ValidationError):
    pass


class ProjectNameNotAvailableForUser(ValidationError):
    pass


class CollidingPomodoroWasFound(ValidationError):
    pass


class FutureDateProvided(ValidationError):
    pass


class NaiveDateProvided(ValidationError):
    pass


class StartDateGreaterThanEndDate(ValidationError):
    pass


class DateFrameIsAlreadyFinished(ValidationError):
    pass


class NoActionAllowedOnFinishedPomodoro(ValidationError):
    pass


class PomodoroErrorMarginExceeded(ValidationError):
    pass


class NoActionAllowedOnCompletedTask(ValidationError):
    pass
