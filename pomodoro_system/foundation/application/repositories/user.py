from abc import ABC, abstractmethod

from foundation.interfaces import AbstractUser
from foundation.value_objects import UserId


class UserRepository(ABC):
    @abstractmethod
    def get(self, user_id: UserId) -> AbstractUser:
        pass

    @abstractmethod
    def save(self, user: AbstractUser, create: bool = False) -> None:
        pass
