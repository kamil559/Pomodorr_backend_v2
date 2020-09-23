import random
import uuid
from datetime import timedelta, datetime

import factory
from factory.fuzzy import FuzzyAttribute

from foundation.tests.factories import UserFactory
from foundation.value_objects import DateFrameDefinition, Priority
from pomodoros.domain.entities import Task, SubTask, Project
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import TaskStatus


class PriorityFactory(factory.Factory):
    class Meta:
        model = Priority

    id = FuzzyAttribute(lambda: uuid.uuid4())
    priority_level = FuzzyAttribute(lambda: random.randint(0, 3))
    color = factory.Faker('color')
    created_at = FuzzyAttribute(lambda: datetime.now())


class ProjectFactory(factory.Factory):
    class Meta:
        model = Project

    id = FuzzyAttribute(lambda: uuid.uuid4())
    name = factory.Faker('name')
    priority = factory.SubFactory(PriorityFactory)
    ordering = factory.Sequence(lambda number: number)
    owner = factory.SubFactory(UserFactory)
    owner_id = factory.LazyAttribute(lambda project: project.owner.id)


class DateFrameDefinitionFactory(factory.Factory):
    class Meta:
        model = DateFrameDefinition

    pomodoro_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(25, 40)))
    break_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(5, 10)))
    longer_break_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(15, 30)))
    gap_between_long_breaks = FuzzyAttribute(lambda: random.randint(4, 7))


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    id = FuzzyAttribute(lambda: uuid.uuid4())
    name = factory.Faker('name')
    status = TaskStatus.ACTIVE
    priority = factory.SubFactory(PriorityFactory)
    ordering = factory.Sequence(lambda number: number)
    due_date = FuzzyAttribute(lambda: datetime.now() + timedelta(days=random.randint(1, 7)))
    pomodoros_to_do = FuzzyAttribute(lambda: random.randint(0, 15))
    pomodoros_burn_down = factory.LazyAttribute(lambda task: random.randint(0, task.pomodoros_to_do))
    reminder_date = factory.LazyAttribute(lambda task: task.due_date - timedelta(days=random.randint(1, 2)))
    renewal_interval = FuzzyAttribute(lambda: timedelta(days=random.randint(1, 7)))
    note = factory.Faker('text')
    created_at = FuzzyAttribute(lambda: datetime.now())


class SubTaskFactory(factory.Factory):
    class Meta:
        model = SubTask

    id = FuzzyAttribute(lambda: uuid.uuid4())
    name = factory.Faker('name')
    task = factory.SubFactory(TaskFactory)
    task_id = factory.LazyAttribute(lambda sub_task: sub_task.task.id)
    created_at = FuzzyAttribute(lambda: datetime.now())
    is_completed = FuzzyAttribute(lambda: bool(random.randint(0, 1)))


class PomodoroFactory(factory.Factory):
    class Meta:
        model = Pomodoro

    id = FuzzyAttribute(lambda: uuid.uuid4())
    task = factory.SubFactory(TaskFactory)
    task_id = factory.LazyAttribute(lambda pomodoro: pomodoro.task.id)


class PauseFactory(factory.Factory):
    class Meta:
        model = Pause

    id = FuzzyAttribute(lambda: uuid.uuid4())
    pomodoro = factory.SubFactory(PomodoroFactory)
    pomodoro_id = factory.LazyAttribute(lambda pause: pause.pomodoro.id)
