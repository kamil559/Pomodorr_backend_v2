import uuid

import factory
from factory.fuzzy import FuzzyAttribute

from foundation.entities.user import AbstractUser
from foundation.value_objects import UserDateFrameDefinition


class UserDateFrameDefinitionFactory(factory.Factory):
    class Meta:
        model = UserDateFrameDefinition


class UserFactory(factory.Factory):
    class Meta:
        model = AbstractUser

    id = FuzzyAttribute(lambda: uuid.uuid4())
    date_frame_definition = factory.SubFactory(UserDateFrameDefinitionFactory)
