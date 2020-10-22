from abc import ABC, abstractmethod

from foundation.value_objects import UserId
from interfaces import AbstractUser


class UsersRepository(ABC):
    @abstractmethod
    def get(self, user_id: UserId) -> AbstractUser:
        pass

    @abstractmethod
    def save(self, user: AbstractUser) -> None:
        pass
