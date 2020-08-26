class InvalidProjectOwner(Exception):
    pass


class TaskNameNotAvailableInNewProject(Exception):
    pass


class TaskAlreadyActive(Exception):
    pass


class TaskAlreadyCompleted(Exception):
    pass


class SubTaskNotAvailableInTask(Exception):
    pass


class ProjectNameNotAvailableForUser(Exception):
    pass
