class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidProjectOwner(ValidationError):
    pass


class TaskNameNotAvailableInNewProject(ValidationError):
    pass


class TaskAlreadyActive(ValidationError):
    pass


class TaskAlreadyCompleted(ValidationError):
    pass


class SubTaskNotAvailableInTask(ValidationError):
    pass


class ProjectNameNotAvailableForUser(ValidationError):
    pass


class CollidingDateFrameFound(ValidationError):
    pass


class FutureDateProvided(ValidationError):
    pass


class NaiveDateProvided(ValidationError):
    pass


class StartDateGreaterThanEndDate(ValidationError):
    pass


class DateFrameAlreadyFinished(ValidationError):
    pass


class PomodoroErrorMarginExceeded(ValidationError):
    pass
