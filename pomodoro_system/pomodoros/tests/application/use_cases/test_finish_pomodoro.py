from datetime import datetime

from pomodoros.application.use_cases.finish_pomodoro import FinishPomodoroInputDto, FinishPomodoroOutputDto


def test_finish_pomodoro_use_case(user, started_pomodoro, finish_pomodoro_output_boundary, finish_pomodoro_use_case,
                                  populated_pomodoros_repository):
    now = datetime.now()
    finish_pomodoro_input_dto = FinishPomodoroInputDto(id=started_pomodoro.id, end_date=now, owner_id=user.id)

    finish_pomodoro_use_case.execute(input_dto=finish_pomodoro_input_dto)
    expected_dto = FinishPomodoroOutputDto(id=started_pomodoro.id, start_date=started_pomodoro.start_date, end_date=now,
                                           frame_type=started_pomodoro.frame_type)

    mutated_pomodoro = populated_pomodoros_repository.get(started_pomodoro.id)

    assert mutated_pomodoro.end_date == now
    finish_pomodoro_output_boundary.present.assert_called_once_with(expected_dto)
