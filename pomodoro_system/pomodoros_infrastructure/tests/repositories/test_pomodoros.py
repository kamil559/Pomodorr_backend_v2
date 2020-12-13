import uuid
from datetime import datetime, timedelta

import pytest
import pytz
from foundation.exceptions import NotFound
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros_infrastructure.repositories import SQLPomodoroRepository
from pony.orm import db_session, flush


@pytest.mark.usefixtures("setup_teardown_tables")
class TestPomodoroRepository:
    @db_session
    def test_repository_returns_mapped_entity(self, orm_pause):
        repo = SQLPomodoroRepository()
        orm_pomodoro = orm_pause.pomodoro
        domain_pause = Pause(orm_pause.id, orm_pause.start_date, orm_pause.end_date)
        expected_entity = Pomodoro(
            orm_pomodoro.id,
            orm_pomodoro.id,
            orm_pomodoro.start_date,
            orm_pomodoro.end_date,
            [
                domain_pause,
            ],
        )

        result = repo.get(orm_pomodoro.id)

        assert expected_entity == result

    @db_session
    def test_repository_raises_error_when_no_pomodoro_was_found(self):
        repo = SQLPomodoroRepository()
        random_uuid = uuid.uuid4()

        with pytest.raises(NotFound):
            repo.get(random_uuid)

    def test_repository_saves_pomodoro_values(self, orm_pause):
        repo = SQLPomodoroRepository()
        orm_pomodoro = orm_pause.pomodoro

        with db_session(strict=True):
            domain_pomodoro = Pomodoro(
                id=orm_pomodoro.id,
                task_id=orm_pomodoro.task.id,
                start_date=orm_pomodoro.start_date,
                end_date=orm_pomodoro.end_date,
                contained_pauses=None,
            )
            new_start_date = datetime.now(tz=pytz.UTC)
            domain_pomodoro.start_date = new_start_date
            new_end_date = domain_pomodoro.start_date + timedelta(minutes=5)
            domain_pomodoro.end_date = new_end_date

            repo.save(domain_pomodoro)
            flush()

        with db_session:
            fetched_pomodoro = repo.get(domain_pomodoro.id)

            assert fetched_pomodoro.start_date == new_start_date
            assert fetched_pomodoro.end_date == new_end_date
