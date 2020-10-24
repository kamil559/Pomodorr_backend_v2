from datetime import datetime

from pomodoros.application.use_cases.resume_pomodoro import (
    ResumePomodoroInputDto,
    ResumePomodoroOutputDto,
)


def test_resume_pomodoro_use_case(paused_pomodoro, resume_pomodoro_output_boundary, resume_pomodoro_use_case):
    now = datetime.now()
    resume_pomodoro_input_dto = ResumePomodoroInputDto(pomodoro_id=paused_pomodoro.id, resume_date=now)

    resume_pomodoro_use_case.execute(input_dto=resume_pomodoro_input_dto)

    expected_output_dto = ResumePomodoroOutputDto(pomodoro_id=paused_pomodoro.id, resume_date=now)

    assert paused_pomodoro.contained_pauses is not None
    assert len(paused_pomodoro.contained_pauses) == 1
    assert paused_pomodoro.contained_pauses[-1].is_finished
    resume_pomodoro_output_boundary.present.assert_called_once_with(expected_output_dto)
