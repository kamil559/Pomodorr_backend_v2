from pomodoros.application.use_cases.reactivate_task import ReactivateTaskInputDto, ReactivateTaskOutputDto
from pomodoros.domain.value_objects import TaskStatus


def test_reactivate_task_test_case(completed_task, reactivate_task_output_boundary, reactivate_task_use_case):
    reactivate_task_input_dto = ReactivateTaskInputDto(id=completed_task.id)
    expected_output_dto = ReactivateTaskOutputDto(id=completed_task.id, status=TaskStatus.ACTIVE)

    reactivate_task_use_case.execute(input_dto=reactivate_task_input_dto)

    assert completed_task.is_active
    reactivate_task_output_boundary.present.assert_called_once_with(expected_output_dto)
