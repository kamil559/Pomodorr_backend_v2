from typing import Dict, List, Union


class RepositoryError(Exception):
    def __init__(self, message: Union[str, List, Dict] = None):
        self.messages = [message] if isinstance(message, (str, bytes)) else message


class NotFound(RepositoryError):
    pass


class AlreadyExists(RepositoryError):
    pass


class DomainValidationError(Exception):
    def __init__(self, message: Union[str, List, Dict] = None):
        self.messages = [message] if isinstance(message, (str, bytes)) else message
