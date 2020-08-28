class ValidationError(Exception):
    pass


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


class CollidingDateFramesFound(ValidationError):
    pass


class FutureDateProvided(ValidationError):
    pass


class NaiveDateProvided(ValidationError):
    pass
