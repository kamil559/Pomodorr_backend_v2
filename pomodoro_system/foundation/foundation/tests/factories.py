import uuid

import factory
from factory.fuzzy import FuzzyAttribute

from foundation.entities.user import AbstractUser
from foundation.value_objects import UserDateFrameDefinition


class UserDateFrameDefinitionFactory(factory.Factory):
    class Meta:
        model = UserDateFrameDefinition

    pomodoro_length = UserDateFrameDefinition.pomodoro_length
    break_length = UserDateFrameDefinition.break_length
    longer_break_length = UserDateFrameDefinition.longer_break_length
    gap_between_long_breaks = UserDateFrameDefinition.gap_between_long_breaks


class UserFactory(factory.Factory):
    class Meta:
        model = AbstractUser

    id = FuzzyAttribute(lambda: uuid.uuid4())
    date_frame_definition = factory.SubFactory(UserDateFrameDefinitionFactory)
