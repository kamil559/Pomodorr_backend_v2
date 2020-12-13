from typing import Any, Mapping, Optional

from foundation.exceptions import ValueValidationError
from foundation.value_objects import Color
from marshmallow import ValidationError, fields


class ColorField(fields.String):
    def _serialize(self, value: Any, attr: str, obj: Any, **kwargs) -> str:
        return getattr(value, "hex", Color().hex)

    def _deserialize(self, value: Any, attr: Optional[str], data: Optional[Mapping[str, Any]], **kwargs) -> Color:
        try:
            color = Color(value)
        except ValueValidationError as error:
            raise ValidationError(error.messages)
        else:
            return color
