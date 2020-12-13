import factory
import pytest
from flask import Flask
from foundation.value_objects import Color
from marshmallow import ValidationError
from pytest_lazyfixture import lazy_fixture
from web_app.utils import get_file_url


class TestColorField:
    def test_serialized_value_is_color_hex(self, color_field_sample_schema):
        color = factory.Faker("color").generate({"locale": "en"})
        deserialized_color_schema_data = color_field_sample_schema().load({"color_field": color})
        serialized_color_schema_data = color_field_sample_schema().dump(deserialized_color_schema_data)
        assert serialized_color_schema_data["color_field"] == color

    def test_deserialized_value_is_color_value_object(self, color_field_sample_schema):
        color = factory.Faker("color").generate({"locale": "en"})
        deserialized_color_schema_data = color_field_sample_schema().load({"color_field": color})

        assert type(deserialized_color_schema_data["color_field"]) == Color
        assert deserialized_color_schema_data["color_field"] == Color(color)


class TestFileField:
    @pytest.mark.parametrize("tested_file", [lazy_fixture("jpg_file"), lazy_fixture("gif_file")])
    def test_serialize_with_valid_file(self, app: Flask, tested_file, file_field_sample_schema):
        with app.test_request_context():
            deserialized_file_schema_data = file_field_sample_schema().load({"file_field": tested_file})
            serialized_file_schema_data = file_field_sample_schema().dump(deserialized_file_schema_data)

            filename = deserialized_file_schema_data["file_field"].filename

            assert serialized_file_schema_data["file_field"] == get_file_url("users.retrieve_avatar", filename)

    @pytest.mark.parametrize("tested_file", [lazy_fixture("invalid_name_image"), lazy_fixture("invalid_content_image")])
    def test_serialize_with_invalid_file(self, app: Flask, tested_file, file_field_sample_schema):
        with pytest.raises(ValidationError) as error:
            file_field_sample_schema().load({"file_field": tested_file})

        assert "Uploaded file's extension is invalid" in error.value.messages["file_field"]
