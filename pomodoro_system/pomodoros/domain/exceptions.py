from foundation.exceptions import DomainValidationError


class InvalidProjectOwner(DomainValidationError):
    pass


class TaskNameNotAvailableInNewProject(DomainValidationError):
    pass


class TaskForDueDateAlreadyExists(DomainValidationError):
    pass


class TaskAlreadyActive(DomainValidationError):
    pass


class TaskAlreadyCompleted(DomainValidationError):
    pass


class SubTaskNotAvailableInTask(DomainValidationError):
    pass


class ProjectNameNotAvailableForUser(DomainValidationError):
    pass


class CollidingPomodoroWasFound(DomainValidationError):
    pass


class StartDateGreaterThanEndDate(DomainValidationError):
    pass


class DateFrameIsAlreadyFinished(DomainValidationError):
    pass


class NoActionAllowedOnFinishedPomodoro(DomainValidationError):
    pass


class PomodoroErrorMarginExceeded(DomainValidationError):
    pass


class NoActionAllowedOnCompletedTask(DomainValidationError):
    pass
