from marshmallow import EXCLUDE, Schema, fields, post_load
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
    banned_until = fields.AwareDateTime(required=True, allow_none=False)
    is_permanent = fields.Boolean(required=True, allow_none=False)
    ban_reason = fields.String(required=False)
    is_active = fields.Boolean(dump_only=True)
    is_banned = fields.Boolean(dump_only=True)

    class Meta:
        unknown = EXCLUDE

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
