import marshmallow_dataclass
from foundation.interfaces import AbstractUser, MediaStorage
from foundation.value_objects import UserDateFrameDefinition
from marshmallow import EXCLUDE, fields, post_dump, post_load, validate
from web_app.marshallers.date_frame_definition import DateFrameDefinitionSchema
from web_app.marshallers.fields.file_field import FileField
from web_app.utils import get_file_url


class UserDateFrameDefinitionSchema(DateFrameDefinitionSchema):
    getting_to_work_sound = fields.String(
        required=True,
        allow_none=False,
        validate=validate.OneOf({"sound_1", "sound_2", "sound_3"}),
    )
    break_time_sound = fields.String(
        required=True,
        allow_none=False,
        validate=validate.OneOf({"sound_1", "sound_2", "sound_3"}),
    )

    @post_dump
    def transform(self, data: dict, **_kwargs) -> dict:
        data["getting_to_work_sound"] = get_file_url(
            "static", f'{data.get("getting_to_work_sound") or UserDateFrameDefinition.getting_to_work_sound}.mp3'
        )
        data["break_time_sound"] = get_file_url(
            "static", f'{data.get("break_time_sound") or UserDateFrameDefinition.break_time_sound}.mp3'
        )
        return data

    @post_load
    def to_dto(self, data: dict, **_kwargs) -> dict:
        return UserDateFrameDefinition(
            pomodoro_length=data.get("pomodoro_length") or UserDateFrameDefinition.pomodoro_length,
            break_length=data.get("break_length") or UserDateFrameDefinition.break_length,
            longer_break_length=data.get("longer_break_length") or UserDateFrameDefinition.longer_break_length,
            gap_between_long_breaks=data.get("gap_between_long_breaks")
            or UserDateFrameDefinition.gap_between_long_breaks,
            getting_to_work_sound=data.get("getting_to_work_sound") or UserDateFrameDefinition.getting_to_work_sound,
            break_time_sound=data.get("break_time_sound") or UserDateFrameDefinition.break_time_sound,
        )

    class Meta:
        unknown = EXCLUDE


BaseUserSchema = marshmallow_dataclass.class_schema(AbstractUser)


class UserSchema(BaseUserSchema):
    id = fields.UUID(dump_only=True)
    email = fields.Email(dump_only=True)
    avatar = FileField(required=False, allow_none=True, retrieve_file_endpoint="users.retrieve_avatar", type="string")
    date_frame_definition = fields.Nested(UserDateFrameDefinitionSchema, required=False, allow_none=True)
    remove_avatar = fields.Boolean(load_only=True, required=False, allow_none=True)

    def __init__(self, media_storage: MediaStorage = None, *args, **kwargs) -> None:
        self.media_storage = media_storage
        super(UserSchema, self).__init__(*args, **kwargs)

    def populate_partial_data(self, request_data: dict) -> dict:
        user_instance = self.context["user_instance"]
        pre_populated_data = {
            "id": user_instance.id,
            "email": user_instance.email,
        }
        request_data.update(pre_populated_data)

        for schema_field in self.fields.keys():
            if hasattr(user_instance, str(schema_field)):
                request_data.setdefault(schema_field, getattr(user_instance, str(schema_field)))
        return request_data

    def update_avatar(self, data: dict) -> str:
        user_instance = self.context["user_instance"]
        remove_avatar = data.pop("remove_avatar", False) or False

        if remove_avatar:
            return str()
        else:
            avatar = data.get("avatar") or str()
            if user_instance.avatar != avatar:
                return user_instance.avatar if not avatar else self.media_storage.save_file(avatar, "avatars")
            return user_instance.avatar

    @post_load
    def populate_and_save_media(self, data: dict, **_kwargs) -> AbstractUser:
        user_data = self.populate_partial_data(data)
        data["avatar"] = self.update_avatar(data)

        data.update(user_data)
        return data

    class Meta:
        unknown = EXCLUDE
        load_only = ("remove_avatar",)
        dump_only = ("id", "email")
