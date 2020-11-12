import uuid
from datetime import datetime, timedelta
from random import randint

import pytest
import pytz
from foundation.exceptions import NotFound
from foundation.utils import with_tzinfo
from foundation.value_objects import DateFrameDefinition, Priority, PriorityLevel
from pomodoros.domain.entities import Task
from pomodoros.domain.value_objects import TaskStatus
from pomodoros_infrastructure import SubTaskModel
from pomodoros_infrastructure.repositories import SQLTaskRepository
from pony.orm import db_session, flush


@pytest.mark.usefixtures("setup_teardown_tables")
class TestSQLTaskRepository:
    @db_session
    def test_repository_returns_mapped_entity(self, orm_task):
        repo = SQLTaskRepository()

        priority = Priority(orm_task.priority_color, PriorityLevel(orm_task.priority_level))
        date_frame_definition = DateFrameDefinition(
            orm_task.pomodoro_length,
            orm_task.break_length,
            orm_task.longer_break_length,
            orm_task.gap_between_long_breaks,
        )

        expected_entity = Task(
            id=orm_task.id,
            project_id=orm_task.project.id,
            name=orm_task.name,
            status=TaskStatus(orm_task.status),
            priority=priority,
            ordering=orm_task.ordering,
            due_date=orm_task.due_date,
            pomodoros_to_do=orm_task.pomodoros_to_do,
            pomodoros_burn_down=orm_task.pomodoros_burn_down,
            date_frame_definition=date_frame_definition,
            reminder_date=orm_task.reminder_date,
            renewal_interval=orm_task.renewal_interval,
            note=orm_task.note,
            created_at=orm_task.created_at,
            sub_tasks=list(
                map(
                    lambda sub_task: SubTaskModel(
                        id=sub_task.id,
                        name=sub_task.name,
                        task=sub_task.task_id,
                        created_at=with_tzinfo(sub_task.created_at),
                        is_completed=sub_task.is_completed,
                    ),
                    orm_task.sub_tasks,
                )
            ),
        )

        result = repo.get(orm_task.id)

        assert result == expected_entity

    @db_session
    def test_repository_raises_error_when_no_task_was_found(self):
        repo = SQLTaskRepository()
        random_uuid = uuid.uuid4()

        with pytest.raises(NotFound):
            repo.get(random_uuid)

    def test_repository_saves_task_values(self, orm_task, orm_second_project):
        repo = SQLTaskRepository()

        values_to_update = {
            "project_id": orm_second_project.id,
            "name": "xyz",
            "status": TaskStatus.COMPLETED,
            "priority": Priority("#952424", PriorityLevel(randint(0, 3))),
            "ordering": 1,
            "due_date": (datetime.now() + timedelta(days=1)).astimezone(tz=pytz.UTC),
            "pomodoros_to_do": 45,
            "date_frame_definition": DateFrameDefinition(
                timedelta(minutes=20),
                timedelta(7),
                timedelta(minutes=13),
                randint(1, 5),
            ),
            "reminder_date": (datetime.now() + timedelta(hours=5)).astimezone(tz=pytz.UTC),
            "renewal_interval": timedelta(days=2),
            "note": "Lorem ipsum",
        }

        with db_session(strict=True):
            domain_task = repo.get(orm_task.id)

            for field, value in values_to_update.items():
                setattr(domain_task, field, value)

            repo.save(domain_task)
            flush()

        with db_session:
            fetched_task = repo.get(domain_task.id)

            assert [getattr(fetched_task, field) for field in values_to_update.keys()] == [
                values_to_update[field] for field in values_to_update.keys()
            ]
