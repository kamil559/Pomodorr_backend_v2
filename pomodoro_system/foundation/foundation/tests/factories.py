import random
from datetime import timedelta

import factory
from factory.fuzzy import FuzzyAttribute

from foundation.value_objects.user import AbstractUser
from foundation.value_objects.user_config import UserConfig


class UserConfigFactory(factory.Factory):
    class Meta:
        model = UserConfig

    pomodoro_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(5, 25)))
    break_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(5, 10)))


class UserFactory(factory.Factory):
    class Meta:
        model = AbstractUser

    projects = factory.List([ProjectFactory(), ProjectFactory()])
    user_config = factory.SubFactory(UserConfigFactory)
