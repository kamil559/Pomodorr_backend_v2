from gettext import gettext as _

from marshmallow import EXCLUDE, Schema, ValidationError, fields, post_load, pre_load
from web_app.users.facade import BanUserInputDto, UnbanUserInputDto


class TokenSchema(Schema):
    id = fields.UUID(dump_only=True)
    revoked = fields.Boolean(required=False, allow_none=True)
    expires = fields.DateTime(dump_only=True)
    browser = fields.String(dump_only=True)
    platform = fields.String(dump_only=True)
    ip_address = fields.String(dump_only=True)

    class Meta:
        unknown = EXCLUDE


class UserBanRecordSchema(Schema):
    user_id = fields.UUID(required=True, allow_none=False)
    banned_until = fields.AwareDateTime(required=False, allow_none=True)
    is_permanent = fields.Boolean(required=False, allow_none=True)
    ban_reason = fields.String(required=False)
    is_active = fields.Boolean(dump_only=True)
    is_banned = fields.Boolean(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def pre_load_data(self, data: dict, *args, **kwargs) -> None:
        banned_until = data.get("banned_until") or None
        is_permanent = data.get("is_permanent") or None

        if banned_until is None and is_permanent is None:
            raise ValidationError({"_schema": _("Either of banned_until or is_permanent must be passed.")})

        if banned_until is not None and is_permanent is not None:
            data["is_permanent"] = False
        return data

    @post_load
    def make_dto(self, data: dict, **_kwargs) -> BanUserInputDto:
        return BanUserInputDto(**data)


class UserUnbanSchema(Schema):
    user_id = fields.UUID(required=True, allow_none=False)
    manually_unbanned = fields.Boolean(dump_only=True)
    manually_unbanned_at = fields.AwareDateTime(required=True, allow_none=False)
    is_active = fields.Boolean(dump_only=True)
    is_banned = fields.Boolean(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def make_dto(self, data: dict, **_kwargs) -> UnbanUserInputDto:
        return UnbanUserInputDto(**data)
