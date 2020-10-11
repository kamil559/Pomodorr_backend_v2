from abc import ABC, abstractmethod

from foundation.domain.entities.user import UserId, AbstractUser


class UsersRepository(ABC):
    @abstractmethod
    def get(self, user_id: UserId) -> AbstractUser:
        pass

    @abstractmethod
    def save(self, user: AbstractUser) -> None:
        pass
