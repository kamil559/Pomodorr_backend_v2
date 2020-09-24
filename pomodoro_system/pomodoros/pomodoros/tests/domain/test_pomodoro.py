from datetime import datetime, timedelta

import pytest
from pytest_lazyfixture import lazy_fixture

from pomodoros.domain.exceptions import NoActionAllowedOnCompletedTask, CollidingPomodoroWasFound, \
    DateFrameIsAlreadyFinished, StartDateGreaterThanEndDate, PomodoroErrorMarginExceeded
from pomodoros.domain.value_objects import AcceptablePomodoroErrorMargin
from pomodoros.tests.factories import PomodoroFactory


@pytest.mark.parametrize(
    'recent_potentially_colliding_pomodoros',
    [
        lazy_fixture('overlapping_unfinished_pomodoros'),
        lazy_fixture('finished_non_overlapping_pomodoros')
    ]
)
def test_begin_pomodoro_successfully(pomodoro, task, recent_potentially_colliding_pomodoros):
    now = datetime.now()
    pomodoro.begin(related_task=task, recent_pomodoros=recent_potentially_colliding_pomodoros,
                   start_date=now)

    assert pomodoro.start_date == now


def test_begin_pomodoro_on_completed_task_fails(completed_task):
    pomodoro = PomodoroFactory(task_id=completed_task)
    now = datetime.now()

    with pytest.raises(NoActionAllowedOnCompletedTask):
        pomodoro.begin(related_task=completed_task, recent_pomodoros=[], start_date=now)


def test_begin_pomodoro_along_colliding_pomodoros_fails(pomodoro, task, overlapping_finished_pomodoros):
    now = datetime.now()

    with pytest.raises(CollidingPomodoroWasFound):
        pomodoro.begin(related_task=task, recent_pomodoros=overlapping_finished_pomodoros, start_date=now)


@pytest.mark.parametrize(
    'recent_potentially_colliding_pomodoros',
    [
        lazy_fixture('overlapping_unfinished_pomodoros'),
        lazy_fixture('finished_non_overlapping_pomodoros')
    ]
)
def test_finish_pomodoro_successfully(date_frame_definition, started_pomodoro, task,
                                      recent_potentially_colliding_pomodoros):
    now = datetime.now()

    started_pomodoro.finish(date_frame_definition=date_frame_definition, related_task=task,
                            recent_pomodoros=recent_potentially_colliding_pomodoros, end_date=now)

    assert started_pomodoro.end_date == now


def test_finish_pomodoro_on_completed_task_fails(date_frame_definition, completed_task):
    now = datetime.now()
    started_pomodoro = PomodoroFactory(task_id=completed_task.id)

    with pytest.raises(NoActionAllowedOnCompletedTask):
        started_pomodoro.finish(date_frame_definition=date_frame_definition, related_task=completed_task,
                                recent_pomodoros=[], end_date=now)


def test_finish_already_finished_pomodoro_fails(date_frame_definition, finished_pomodoro, task):
    now = datetime.now()

    with pytest.raises(DateFrameIsAlreadyFinished):
        finished_pomodoro.finish(date_frame_definition=date_frame_definition, related_task=task, recent_pomodoros=[],
                                 end_date=now)


def test_pomodoro_with_start_date_greater_than_end_date_fails(date_frame_definition, started_pomodoro, task):
    end_date = started_pomodoro.start_date - timedelta(seconds=1)
    with pytest.raises(StartDateGreaterThanEndDate):
        started_pomodoro.finish(date_frame_definition=date_frame_definition, related_task=task, recent_pomodoros=[],
                                end_date=end_date)


def test_finish_pomodoro_with_exceeding_duration_fails(date_frame_definition, started_pomodoro, task):
    maximal_valid_end_date: datetime = started_pomodoro.start_date + \
                                       date_frame_definition.pomodoro_length + AcceptablePomodoroErrorMargin
    exceeded_end_date = maximal_valid_end_date + timedelta(microseconds=1)

    with pytest.raises(PomodoroErrorMarginExceeded):
        started_pomodoro.finish(date_frame_definition=date_frame_definition, related_task=task, recent_pomodoros=[],
                                end_date=exceeded_end_date)


def test_finish_pomodoro_with_exceeding_duration_fitting_within_error_margin_succeeds(date_frame_definition,
                                                                                      started_pomodoro, task):
    maximal_valid_end_date: datetime = started_pomodoro.start_date + \
                                       date_frame_definition.pomodoro_length + AcceptablePomodoroErrorMargin
    started_pomodoro.finish(date_frame_definition=date_frame_definition, related_task=task, recent_pomodoros=[],
                            end_date=maximal_valid_end_date)

    assert started_pomodoro.end_date == maximal_valid_end_date


def test_finish_pomodoro_along_colliding_pomodoros_fails(date_frame_definition, started_pomodoro,
                                                         task, overlapping_finished_pomodoros):
    now = datetime.now()

    with pytest.raises(CollidingPomodoroWasFound):
        started_pomodoro.finish(date_frame_definition=date_frame_definition, related_task=task,
                                recent_pomodoros=overlapping_finished_pomodoros, end_date=now)
