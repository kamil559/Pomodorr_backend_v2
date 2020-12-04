from typing import Optional, Type

from foundation.application.repositories.user import UserRepository
from foundation.exceptions import NotFound
from foundation.i18n import N_
from foundation.interfaces import AbstractUser
from foundation.models import User
from foundation.value_objects import UserDateFrameDefinition, UserId
from pony.orm import ObjectNotFound


class SQLUserRepository(UserRepository):
    @staticmethod
    def _to_entity(user_model: Type[User]) -> AbstractUser:
        return AbstractUser(
            id=user_model.id,
            email=user_model.email,
            avatar=user_model.avatar,
            date_frame_definition=UserDateFrameDefinition(
                pomodoro_length=user_model.date_frame_definition.pomodoro_length,
                break_length=user_model.date_frame_definition.break_length,
                longer_break_length=user_model.date_frame_definition.longer_break_length,
                gap_between_long_breaks=user_model.date_frame_definition.gap_between_long_breaks,
                getting_to_work_sound=user_model.date_frame_definition.getting_to_work_sound,
                break_time_sound=user_model.date_frame_definition.break_time_sound,
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
            "avatar": user.avatar,
            "date_frame_definition": {
                "pomodoro_length": user.date_frame_definition.pomodoro_length,
                "break_length": user.date_frame_definition.break_length,
                "longer_break_length": user.date_frame_definition.longer_break_length,
                "gap_between_long_breaks": user.date_frame_definition.gap_between_long_breaks,
                "getting_to_work_sound": user.date_frame_definition.getting_to_work_sound,
                "break_time_sound": user.date_frame_definition.break_time_sound,
            },
        }
        orm_user = self._get_for_update(user.id)

        if orm_user is not None:
            orm_user.avatar = values_to_update["avatar"]
            date_frame_definition = orm_user.date_frame_definition
            date_frame_definition.set(**values_to_update["date_frame_definition"])
