from datetime import datetime

from pomodoros.application.use_cases.pause_pomodoro import PausePomodoroInputDto, PausePomodoroOutputDto


def test_pause_pomodoro(started_pomodoro, pause_pomodoro_output_boundary, pause_pomodoro_use_case):
    now = datetime.now()
    pause_pomodoro_input_dto = PausePomodoroInputDto(pomodoro_id=started_pomodoro.id, pause_date=now)

    pause_pomodoro_use_case.execute(input_dto=pause_pomodoro_input_dto)

    expected_output_dto = PausePomodoroOutputDto(pomodoro_id=started_pomodoro.id, pause_date=now)
    pause_pomodoro_output_boundary.present.assert_called_once_with(expected_output_dto)
    assert started_pomodoro.contained_pauses is not None
