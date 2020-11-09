from typing import Type

from foundation.application.repositories.user import UserRepository
from foundation.exceptions import AlreadyExists, NotFound
from foundation.interfaces import AbstractUser
from foundation.models import User
from foundation.value_objects import DateFrameDefinition, UserDateFrameDefinition, UserId
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
            raise NotFound()
        else:
            return self._to_entity(orm_user)

    @staticmethod
    def _get_orm_instance(user_id: UserId) -> Type[User]:
        orm_user = User.get_for_update(id=user_id)

        if orm_user is None:
            raise NotFound()
        return orm_user

    @staticmethod
    def _persist_new_orm_user(user: AbstractUser) -> Type[User]:
        if User.exists(id=user.id):
            raise AlreadyExists()
        else:
            orm_date_frame_definition = UserDateFrameDefinition(
                pomodoro_length=user.date_frame_definition.pomodoro_length,
                break_length=user.date_frame_definition.break_length,
                longer_break_length=user.date_frame_definition.longer_break_length,
                gap_between_long_breaks=user.date_frame_definition.gap_between_long_breaks,
            )
            return User(id=user.id, date_frame_definition=orm_date_frame_definition)

    def save(self, user: AbstractUser, create: bool = False) -> None:
        if create:
            self._persist_new_orm_user(user)
        else:
            values_to_update = {
                "date_frame_definition": {
                    "pomodoro_length": user.date_frame_definition.pomodoro_length,
                    "break_length": user.date_frame_definition.break_length,
                    "longer_break_length": user.date_frame_definition.longer_break_length,
                    "gap_between_long_breaks": user.date_frame_definition.gap_between_long_breaks,
                }
            }
            orm_user = self._get_orm_instance(user.id)
            date_frame_definition = orm_user.date_frame_definition
            date_frame_definition.set(**values_to_update["date_frame_definition"])
