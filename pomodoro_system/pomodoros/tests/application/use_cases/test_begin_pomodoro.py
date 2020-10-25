from datetime import datetime

from pomodoros.application.use_cases.begin_pomodoro import BeginPomodoroInputDto, BeginPomodoroOutputDto
from pomodoros.domain.value_objects import FrameType


def test_begin_pomodoro_use_case(task, begin_pomodoro_output_boundary, begin_pomodoro_use_case, pomodoros_repository):
    now = datetime.now()
    begin_pomodoro_input_dto = BeginPomodoroInputDto(task_id=task.id, start_date=now)

    begin_pomodoro_use_case.execute(input_dto=begin_pomodoro_input_dto)
    new_pomodoro = list(pomodoros_repository.rows.values())[0]
    expected_output_dto = BeginPomodoroOutputDto(id=new_pomodoro.id, start_date=now, frame_type=FrameType.TYPE_POMODORO)

    assert new_pomodoro.task_id == task.id
    begin_pomodoro_output_boundary.present.assert_called_once_with(expected_output_dto)
