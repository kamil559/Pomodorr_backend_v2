import uuid
from datetime import datetime
from random import randint

import pytest
import pytz
from pony.orm import db_session, flush

from foundation.exceptions import NotFound
from foundation.value_objects import Priority, PriorityLevel
from pomodoros.domain.entities import Project
from pomodoros_infrastructure.repositories import SQLProjectRepository


@pytest.mark.usefixtures("setup_teardown_tables")
class TestSQLProjectRepository:
    @db_session
    def test_repository_returns_mapped_entity(self, orm_project):
        repo = SQLProjectRepository()

        priority = Priority(orm_project.priority_color, PriorityLevel(orm_project.priority_level))
        expected_entity = Project(
            orm_project.id,
            orm_project.name,
            priority,
            orm_project.ordering,
            orm_project.owner_id,
            orm_project.created_at,
            None,
        )

        result = repo.get(orm_project.id)

        assert result == expected_entity

    @db_session
    def test_repository_raises_error_when_no_project_was_found(self):
        repo = SQLProjectRepository()
        random_uuid = uuid.uuid4()

        with pytest.raises(NotFound):
            repo.get(random_uuid)

    def test_repository_saves_project_values(self, orm_project):
        repo = SQLProjectRepository()

        values_to_update = {
            "name": "xyz",
            "priority": Priority("#952424", PriorityLevel(randint(0, 3))),
            "ordering": 1,
            "deleted_at": datetime.now().astimezone(tz=pytz.UTC),
        }

        with db_session(strict=True):
            domain_project = repo.get(orm_project.id)

            for key, value in values_to_update.items():
                setattr(domain_project, key, value)

            repo.save(domain_project)
            flush()

        with db_session:
            fetched_project = repo.get(domain_project.id)

            assert [getattr(fetched_project, field) for field in values_to_update.keys()] == [
                values_to_update[field] for field in values_to_update.keys()
            ]
