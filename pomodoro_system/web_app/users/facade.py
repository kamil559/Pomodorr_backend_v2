from dataclasses import dataclass
from datetime import datetime
from gettext import gettext as _
from typing import Optional, Type
from uuid import UUID

from flask import current_app
from flask_jwt_extended import get_jwt_identity
from foundation.exceptions import DomainValidationError
from foundation.models.user import User, UserBanRecord
from foundation.value_objects import UserId
from pony.orm import db_session
from web_app.authentication.helpers import revoke_all_tokens
from werkzeug.local import LocalProxy

_security = LocalProxy(lambda: current_app.extensions["security"])

_datastore = LocalProxy(lambda: _security.datastore)


@dataclass()
class BanUserInputDto:
    user_id: UserId
    banned_until: Optional[datetime]
    is_permanent: bool
    ban_reason: str


@dataclass
class BanUserOutputDto:
    user_id: UserId
    banned_until: Optional[datetime]
    is_permanent: bool
    ban_reason: str
    is_active: bool
    is_banned: bool


@dataclass
class UnbanUserInputDto:
    user_id: UserId
    manually_unbanned_at: datetime


@dataclass
class UnbanUserOutputDto:
    user_id: UserId
    is_active: bool
    is_banned: bool
    manually_unbanned: bool
    manually_unbanned_at: datetime


class UserFacade:
    @staticmethod
    def executes_self_action(user_id: UserId) -> bool:
        current_user_id = get_jwt_identity()
        return user_id == UUID(current_user_id)

    @db_session
    def ban_user(self, input_dto: BanUserInputDto) -> BanUserOutputDto:
        user = _datastore.get_user(input_dto.user_id, consider_banned=True, raise_if_not_found=True)

        if self.executes_self_action(user.id):
            raise DomainValidationError({"msg": _("You cannot ban yourself.")})

        if user.is_banned:
            raise DomainValidationError({"msg": _("The user is already banned.")})

        user.active = False
        ban_record = UserBanRecord(
            user=user,
            banned_until=input_dto.banned_until,
            is_permanent=input_dto.is_permanent,
            ban_reason=input_dto.ban_reason,
        )
        user.ban_records.add(ban_record)

        revoke_all_tokens(input_dto.user_id)

        self.send_ban_email(user, ban_record)

        return BanUserOutputDto(
            user_id=user.id,
            banned_until=input_dto.banned_until,
            is_permanent=input_dto.is_permanent,
            ban_reason=input_dto.ban_reason,
            is_active=False,
            is_banned=True,
        )

    @db_session
    def unban_user(self, input_dto: UnbanUserInputDto) -> UnbanUserOutputDto:
        user = _datastore.get_user(input_dto.user_id, consider_banned=True, raise_if_not_found=True)

        if self.executes_self_action(user.id):
            raise DomainValidationError({"msg": _("You cannot unban yourself.")})

        if not user.is_banned:
            raise DomainValidationError({"msg": _("The user is not currently banned.")})

        user.active = True
        ban_record = user.current_ban_record
        ban_record.manually_unbanned = True
        ban_record.manually_unbanned_at = input_dto.manually_unbanned_at

        self.send_unban_mail(user, input_dto.manually_unbanned_at)

        return UnbanUserOutputDto(
            user_id=user.id,
            is_active=True,
            is_banned=False,
            manually_unbanned=True,
            manually_unbanned_at=input_dto.manually_unbanned_at,
        )

    @staticmethod
    def send_unban_mail(user, manually_unbanned_at):
        _security._send_mail(
            subject=_("Account unblocked"),
            recipient=user.email,
            template="user_unbanned",
            email=user.email,
            manually_unbanned_at=manually_unbanned_at,
        )

    @staticmethod
    def send_ban_email(user: Type[User], ban_record: Type[UserBanRecord]) -> None:
        _security._send_mail(
            subject=_("Account blocked"),
            recipient=user.email,
            template="user_banned",
            email=user.email,
            ban_reason=ban_record.ban_reason,
            is_permanent=ban_record.is_permanent,
            banned_until=ban_record.banned_until,
        )
