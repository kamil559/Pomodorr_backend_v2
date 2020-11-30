from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Type
from uuid import UUID

from flask import current_app
from flask_jwt_extended import get_jwt_identity
from foundation.exceptions import DomainValidationError
from foundation.i18n import N_
from foundation.models.user import User, UserBanRecord
from foundation.value_objects import UserId
from pony.orm import db_session
from web_app.authentication.helpers import (
    check_can_change_email_address,
    executes_self_action,
    generate_email_change_link,
    revoke_all_tokens,
)
from werkzeug.local import LocalProxy

_security = LocalProxy(lambda: current_app.extensions["security"])

_datastore = LocalProxy(lambda: _security.datastore)


@dataclass
class ChangeEmailInputDto:
    new_email: str
    requested_at: datetime


@dataclass
class ChangeEmailOutputDto:
    new_email: str
    status: str


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
    @db_session
    def request_email_address_change(self, input_dto: ChangeEmailInputDto) -> ChangeEmailOutputDto:
        user = _datastore.get_user(UUID(get_jwt_identity()))

        check_can_change_email_address(new_email=input_dto.new_email)
        user.unconfirmed_new_email = input_dto.new_email
        self.send_change_email_confirmation_email(user, input_dto.new_email, input_dto.requested_at)

        return ChangeEmailOutputDto(
            new_email=input_dto.new_email,
            status=N_("Confirmation instructions have been sent to %(email)s.") % {"email": user.email},
        )

    @db_session
    def change_email(self, user: User) -> None:
        check_can_change_email_address(new_email=user.unconfirmed_new_email)
        user.email = user.unconfirmed_new_email
        user.unconfirmed_new_email = str()
        revoke_all_tokens(user.id)

    @db_session
    def ban_user(self, input_dto: BanUserInputDto) -> BanUserOutputDto:
        user = _datastore.get_user(input_dto.user_id, consider_banned=True, raise_if_not_found=True)

        if executes_self_action(user.id):
            raise DomainValidationError({"msg": N_("You cannot ban yourself.")})

        if user.is_banned:
            raise DomainValidationError({"msg": N_("The user is already banned.")})

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

        if executes_self_action(user.id):
            raise DomainValidationError({"msg": N_("You cannot unban yourself.")})

        if not user.is_banned:
            raise DomainValidationError({"msg": N_("The user is not currently banned.")})

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

    def send_change_email_confirmation_email(self, user: User, new_email: str, requested_at: datetime) -> None:
        confirmation_link = generate_email_change_link(user)

        _security._send_mail(
            subject=N_("Email change request"),
            recipient=user.email,
            template="email_change_request",
            email=user.email,
            new_email=new_email,
            requested_at=requested_at,
            confirmation_link=confirmation_link,
        )

    @staticmethod
    def send_ban_email(user: Type[User], ban_record: Type[UserBanRecord]) -> None:
        _security._send_mail(
            subject=N_("Account blocked"),
            recipient=user.email,
            template="user_banned",
            email=user.email,
            ban_reason=ban_record.ban_reason,
            is_permanent=ban_record.is_permanent,
            banned_until=ban_record.banned_until,
        )

    @staticmethod
    def send_unban_mail(user, manually_unbanned_at) -> None:
        _security._send_mail(
            subject=N_("Account unblocked"),
            recipient=user.email,
            template="user_unbanned",
            email=user.email,
            manually_unbanned_at=manually_unbanned_at,
        )
