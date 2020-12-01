from typing import Optional, Type

from foundation.application.repositories.user import UserRepository
from foundation.exceptions import NotFound
from foundation.i18n import N_
from foundation.interfaces import AbstractUser
from foundation.models import User
from foundation.value_objects import DateFrameDefinition, UserId
from pony.orm import ObjectNotFound


class SQLUserRepository(UserRepository):
    @staticmethod
    def _to_entity(user_model: Type[User]) -> AbstractUser:
        return AbstractUser(
            id=user_model.id,
            date_frame_definition=DateFrameDefinition(
                pomodoro_length=user_model.date_frame_definition.pomodoro_length,
                break_length=user_model.date_frame_definition.break_length,
                longer_break_length=user_model.date_frame_definition.longer_break_length,
                gap_between_long_breaks=user_model.date_frame_definition.gap_between_long_breaks,
            ),
        )

    def get(self, user_id: UserId) -> AbstractUser:
        try:
            orm_user = User[user_id]
        except ObjectNotFound:
            raise NotFound(N_("User does not exist"))
        else:
            return self._to_entity(orm_user)

    @staticmethod
    def _get_for_update(user_id: UserId) -> Optional[Type[User]]:
        return User.get_for_update(id=user_id)

    def save(self, user: AbstractUser, create: bool = False) -> None:
        values_to_update = {
            "date_frame_definition": {
                "pomodoro_length": user.date_frame_definition.pomodoro_length,
                "break_length": user.date_frame_definition.break_length,
                "longer_break_length": user.date_frame_definition.longer_break_length,
                "gap_between_long_breaks": user.date_frame_definition.gap_between_long_breaks,
            }
        }
        orm_user = self._get_for_update(user.id)

        if orm_user is not None:
            date_frame_definition = orm_user.date_frame_definition
            date_frame_definition.set(**values_to_update["date_frame_definition"])
