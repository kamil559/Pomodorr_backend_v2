from marshmallow import EXCLUDE, Schema, fields


class TokenSchema(Schema):
    id = fields.UUID(dump_only=True)
    revoked = fields.Boolean(required=False, allow_none=True)
    expires = fields.DateTime(dump_only=True)
    browser = fields.String(dump_only=True)
    platform = fields.String(dump_only=True)
    ip_address = fields.String(dump_only=True)

    class Meta:
        unknown = EXCLUDE
