from datetime import datetime

from pomodoros.application.use_cases.complete_task import CompleteTaskInputDto, CompleteTaskOutputDto
from pomodoros.domain.value_objects import TaskStatus


def test_complete_task_use_case_with_one_time_task(
    one_time_task, complete_task_output_boundary, complete_task_use_case
):
    now = datetime.now()
    complete_task_input_dto = CompleteTaskInputDto(id=one_time_task.id, completed_at=now)
    complete_task_use_case.execute(input_dto=complete_task_input_dto)

    expected_output_dto = CompleteTaskOutputDto(id=one_time_task.id, status=TaskStatus.COMPLETED, new_task_id=None)

    assert one_time_task.status == TaskStatus.COMPLETED
    complete_task_output_boundary.present.assert_called_once_with(expected_output_dto)


def test_complete_task_use_case_with_repeatable_task(
    task,
    complete_task_output_boundary,
    complete_task_use_case,
    populated_tasks_repository,
):
    now = datetime.now()
    complete_task_input_dto = CompleteTaskInputDto(id=task.id, completed_at=now)
    complete_task_use_case.execute(input_dto=complete_task_input_dto)

    next_due_date_task = list(populated_tasks_repository.rows.values())[-1]
    expected_output_dto = CompleteTaskOutputDto(
        id=task.id, status=TaskStatus.COMPLETED, new_task_id=next_due_date_task.id
    )

    assert task.id != next_due_date_task.id
    assert task.status == TaskStatus.COMPLETED
    complete_task_output_boundary.present.assert_called_once_with(expected_output_dto)
