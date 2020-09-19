import random
import uuid
from datetime import timedelta, datetime

import factory
from factory.fuzzy import FuzzyAttribute

from foundation.tests.factories import UserFactory
from pomodoros.domain.entities import Task, Priority, SubTask, Project
from pomodoros.domain.value_objects import TaskStatus


class PriorityFactory(factory.Factory):
    class Meta:
        model = Priority

    id = FuzzyAttribute(lambda: uuid.uuid4())
    name = factory.Faker('name')
    priority_level = FuzzyAttribute(lambda: random.randint(1, 5))
    color = factory.Faker('color')
    owner = factory.SubFactory(UserFactory)
    created_at = FuzzyAttribute(lambda: datetime.now())


class ProjectFactory(factory.Factory):
    class Meta:
        model = Project

    id = FuzzyAttribute(lambda: uuid.uuid4())
    name = factory.Faker('name')
    priority = factory.SubFactory(PriorityFactory)
    ordering = factory.Sequence(lambda number: number)
    owner = factory.LazyAttribute(lambda project: project.priority.owner)
    is_completed = FuzzyAttribute(lambda: bool(random.randint(0, 1)))


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    id = FuzzyAttribute(lambda: uuid.uuid4())
    name = factory.Faker('name')
    status = TaskStatus.ACTIVE
    priority = factory.SubFactory(PriorityFactory)
    ordering = factory.Sequence(lambda number: number)
    pomodoros_to_do = FuzzyAttribute(lambda: random.randint(0, 15))
    pomodoro_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(5, 25)))
    break_length = FuzzyAttribute(lambda: timedelta(minutes=random.randint(5, 10)))
    due_date = FuzzyAttribute(lambda: datetime.now() + timedelta(days=random.randint(1, 7)))
    reminder_date = FuzzyAttribute(lambda: datetime.now() + timedelta(days=random.randint(1, 3)))
    renewal_interval = FuzzyAttribute(lambda: timedelta(days=random.randint(1, 7)))
    project = factory.LazyAttribute(lambda task: task.priority.owner.projects[0])
    note = factory.Faker('text')
    created_at = FuzzyAttribute(lambda: datetime.now())
    completed_at = factory.LazyAttribute(lambda task: datetime.now() if task.is_active else None)


class SubTaskFactory(factory.Factory):
    class Meta:
        model = SubTask

    id = FuzzyAttribute(lambda: uuid.uuid4())
    name = factory.Faker('name')
    task = factory.SubFactory(TaskFactory)
    created_at = FuzzyAttribute(lambda: datetime.now())
    is_completed = FuzzyAttribute(lambda: bool(random.randint(0, 1)))
