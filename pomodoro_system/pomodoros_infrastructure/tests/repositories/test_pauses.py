import uuid
from datetime import datetime, timedelta

import pytest
import pytz
from pony.orm import db_session, flush

from foundation.exceptions import NotFound
from pomodoros.domain.entities.pause import Pause
from pomodoros_infrastructure.repositories import SQLPauseRepository


@pytest.mark.usefixtures("setup_teardown_tables")
class TestPauseRepository:
    @db_session
    def test_repository_returns_mapped_entity(self, orm_pause):
        repo = SQLPauseRepository()
        expected_entity = Pause(orm_pause.id, orm_pause.start_date, orm_pause.end_date)
        result = repo.get(orm_pause.id)

        assert result == expected_entity

    @db_session
    def test_repository_raises_error_when_no_pause_was_found(self):
        repo = SQLPauseRepository()
        random_uuid = uuid.uuid4()

        with pytest.raises(NotFound):
            repo.get(random_uuid)

    def test_repository_saves_pause_values(self, orm_pause):
        repo = SQLPauseRepository()

        with db_session(strict=True):
            domain_entity = Pause(orm_pause.id, orm_pause.start_date, orm_pause.end_date)
            new_start_date = datetime.now(tz=pytz.UTC)
            domain_entity.start_date = new_start_date
            new_end_date = domain_entity.start_date + timedelta(minutes=5)
            domain_entity.end_date = new_end_date

            repo.save(domain_entity)
            flush()

        with db_session:
            fetched_pause = repo.get(domain_entity.id)

        assert fetched_pause.start_date == new_start_date
        assert fetched_pause.end_date == new_end_date
