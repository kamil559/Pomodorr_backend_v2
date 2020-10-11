class RepositoryError(Exception):
    def __init__(self, message: str = None) -> None:
        self.message = message


class NotFound(RepositoryError):
    pass
