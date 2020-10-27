import uuid
from datetime import datetime

import factory
from factory.fuzzy import FuzzyAttribute
from foundation.interfaces import AbstractUser
from foundation.models import User
from foundation.models import UserDateFrameDefinition as UserDateFrameDefinitionModel
from foundation.models import db
from foundation.value_objects import UserDateFrameDefinition


class PonyOptions(factory.base.FactoryOptions):
    def _build_default_options(self):
        return super()._build_default_options() + [
            factory.base.OptionDefault("db", None, inherit=True),
        ]


class PonyFactory(factory.base.Factory):
    _options_class = PonyOptions

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        db = cls._meta.db
        obj = model_class(*args, **kwargs)
        db.flush()
        return obj


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

    id = factory.LazyFunction(uuid.uuid4)
    date_frame_definition = factory.SubFactory(UserDateFrameDefinitionFactory)


class ORMUserDateFrameDefinitionFactory(PonyFactory):
    class Meta:
        model = UserDateFrameDefinitionModel
        db = db

    id = factory.LazyFunction(uuid.uuid4)
    pomodoro_length = UserDateFrameDefinition.pomodoro_length
    break_length = UserDateFrameDefinition.break_length
    longer_break_length = UserDateFrameDefinition.longer_break_length
    gap_between_long_breaks = UserDateFrameDefinition.gap_between_long_breaks

    user = FuzzyAttribute(lambda: ORMUserFactory())


class ORMUserFactory(PonyFactory):
    class Meta:
        model = User
        db = db

    id = factory.LazyFunction(uuid.uuid4)
    confirmed_at = factory.LazyFunction(datetime.now)
    email = factory.Faker("email")
    password = factory.Faker("password", length=36, special_chars=True, digits=True, upper_case=True, lower_case=True)
    date_frame_definition = None
    active = False
