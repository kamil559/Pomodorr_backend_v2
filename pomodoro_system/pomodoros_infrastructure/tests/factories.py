import random
import uuid
from datetime import datetime, timedelta

import factory
import pytz
from factory.fuzzy import FuzzyAttribute
from foundation.models import db
from foundation.tests.factories import ORMUserFactory, PonyFactory
from pomodoros.domain.value_objects import FrameType, TaskStatus
from pomodoros_infrastructure import PauseModel, PomodoroModel, ProjectModel, SubTaskModel, TaskModel


class ORMProjectFactory(PonyFactory):
    class Meta:
        model = ProjectModel
        db = db

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("name")
    priority_color = factory.Faker("color")
    priority_level = FuzzyAttribute(lambda: random.randint(0, 3))
    ordering = factory.Sequence(lambda number: number)
    owner = factory.LazyAttribute(lambda project: ORMUserFactory().id)
    created_at = FuzzyAttribute(lambda: datetime.now(tz=pytz.UTC))
    deleted_at = None
    tasks = []


class ORMSubTaskFactory(PonyFactory):
    class Meta:
        model = SubTaskModel
        db = db

    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Faker("name")
    task_id = FuzzyAttribute(lambda: ORMTaskFactory().id)
    created_at = FuzzyAttribute(lambda: datetime.now(tz=pytz.UTC))
    is_completed = FuzzyAttribute(lambda: bool(random.randint(0, 1)))


class ORMTaskFactory(PonyFactory):
    class Meta:
        model = TaskModel
        db = db

    id = factory.LazyFunction(uuid.uuid4)
    project = FuzzyAttribute(lambda: ORMProjectFactory())
    name = factory.Faker("name")
    status = TaskStatus.ACTIVE.value
    priority_color = factory.Faker("color")
    priority_level = FuzzyAttribute(lambda: random.randint(0, 3))
    ordering = factory.Sequence(lambda number: number)
    due_date = FuzzyAttribute(lambda: datetime.now(tz=pytz.UTC))
    pomodoros_to_do = FuzzyAttribute(lambda: random.randint(0, 15))
    pomodoros_burn_down = factory.LazyAttribute(lambda task: random.randint(0, task.pomodoros_to_do))
    pomodoro_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(25, 40)))
    break_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(5, 10)))
    longer_break_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(15, 30)))
    gap_between_long_breaks = FuzzyAttribute(lambda: random.randint(4, 7))
    reminder_date = factory.LazyAttribute(lambda task: task.due_date - timedelta(days=random.randint(1, 2)))
    renewal_interval = FuzzyAttribute(lambda: timedelta(days=random.randint(1, 7)))
    note = factory.Faker("text")
    created_at = FuzzyAttribute(lambda: datetime.now(tz=pytz.UTC))
    sub_tasks = factory.List([])


class ORMPomodoroFactory(PonyFactory):
    class Meta:
        model = PomodoroModel
        db = db

    id = factory.LazyFunction(uuid.uuid4)
    frame_type = FrameType.TYPE_POMODORO.value
    task = FuzzyAttribute(lambda: ORMTaskFactory())
    start_date = FuzzyAttribute(lambda: datetime.now(tz=pytz.UTC).replace(hour=12, minute=0))
    end_date = FuzzyAttribute(lambda: datetime.now(tz=pytz.UTC).replace(hour=12, minute=30))
    contained_pauses = factory.List([])


class ORMPauseFactory(PonyFactory):
    class Meta:
        model = PauseModel
        db = db

    id = factory.LazyFunction(uuid.uuid4)
    frame_type = FrameType.TYPE_PAUSE.value
    start_date = FuzzyAttribute(lambda: datetime.now(tz=pytz.UTC) + timedelta(minutes=5))
    end_date = factory.LazyAttribute(lambda pause: pause.start_date + timedelta(minutes=5))
    pomodoro = factory.SubFactory(ORMPomodoroFactory)
