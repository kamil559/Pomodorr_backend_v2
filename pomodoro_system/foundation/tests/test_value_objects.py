import pytest
from foundation.exceptions import ValueValidationError
from foundation.value_objects import Color, DefaultColorHex


class TestColorValueObject:
    @pytest.mark.parametrize(
        "tested_value",
        ["#d2d2d2", "#FFF", "#000"],
    )
    def test_create_color_with_valid_values(self, tested_value):
        color = Color(tested_value)

        assert color.hex == tested_value

    def test_create_color_with_no_arguments_returns_default_color(self):
        color = Color()

        assert color.hex == DefaultColorHex

    @pytest.mark.parametrize("invalid_value", [123, b"123", 1.25, ["#d1d1d1"]])
    def test_create_color_with_non_string_hex_fails(self, invalid_value):
        with pytest.raises(ValueValidationError) as error:
            Color(invalid_value)

            assert error.message == "Color type must be string."

    @pytest.mark.parametrize("invalid_string", ["red", "d1d1d1", "#d1d1d1d1", "##d1d1d1"])
    def test_create_color_with_invalid_value_fails(self, invalid_string):
        with pytest.raises(ValueValidationError) as error:
            Color("")

            assert error.message == "Invalid rgb hex value."
