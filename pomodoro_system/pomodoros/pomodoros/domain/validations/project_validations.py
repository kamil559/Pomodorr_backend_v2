from pomodoros.domain.exceptions import ProjectNameNotAvailableForUser
from users.domain.entities import AbstractUser


def check_project_name_available_for_user(user: AbstractUser, project_name: str) -> None:
    user_project = list(filter(lambda project: project.name == project_name, user.projects))

    if len(user_project):
        raise ProjectNameNotAvailableForUser
