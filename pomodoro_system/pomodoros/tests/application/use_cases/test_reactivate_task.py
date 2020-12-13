import pytest
from pomodoros.application.use_cases.reactivate_task import (
    ReactivateTask,
    ReactivateTaskInputDto,
    ReactivateTaskOutputDto,
)
from pomodoros.domain.exceptions import TaskNameNotAvailableInNewProject
from pomodoros.domain.value_objects import TaskStatus


def test_reactivate_task(
    completed_task, reactivate_task_output_boundary, populated_tasks_repository, populated_tasks_by_project_id_query
):
    reactivate_task_input_dto = ReactivateTaskInputDto(id=completed_task.id)
    expected_output_dto = ReactivateTaskOutputDto(id=completed_task.id, status=TaskStatus.ACTIVE)

    reactivate_task_use_case = ReactivateTask(
        output_boundary=reactivate_task_output_boundary,
        tasks_repository=populated_tasks_repository,
        get_recent_tasks_by_pomodoro_id_query=populated_tasks_by_project_id_query,
    )
    reactivate_task_use_case.execute(input_dto=reactivate_task_input_dto)

    assert completed_task.is_active
    reactivate_task_output_boundary.present.assert_called_once_with(expected_output_dto)


def test_reactivate_task_with_duplicate_task_for_the_due_date_fails(
    completed_task,
    duplicate_active_task,
    reactivate_task_output_boundary,
    populated_tasks_repository_with_duplicates,
    populated_tasks_by_project_id_query_with_duplicates,
):
    reactivate_task_input_dto = ReactivateTaskInputDto(id=completed_task.id)

    reactivate_task_use_case = ReactivateTask(
        reactivate_task_output_boundary,
        populated_tasks_repository_with_duplicates,
        populated_tasks_by_project_id_query_with_duplicates,
    )

    with pytest.raises(TaskNameNotAvailableInNewProject):
        reactivate_task_use_case.execute(reactivate_task_input_dto)


def test_reactivate_task_with_duplicate_task_in_the_past_succeeds(
    completed_task,
    duplicate_active_task,
    reactivate_task_output_boundary,
    populated_tasks_repository_with_duplicates_in_the_past,
    populated_tasks_by_project_id_query_with_duplicates_in_the_past,
):
    reactivate_task_input_dto = ReactivateTaskInputDto(id=completed_task.id)
    expected_output_dto = ReactivateTaskOutputDto(id=completed_task.id, status=TaskStatus.ACTIVE)

    reactivate_task_use_case = ReactivateTask(
        reactivate_task_output_boundary,
        populated_tasks_repository_with_duplicates_in_the_past,
        populated_tasks_by_project_id_query_with_duplicates_in_the_past,
    )
    reactivate_task_use_case.execute(input_dto=reactivate_task_input_dto)

    assert completed_task.is_active
    reactivate_task_output_boundary.present.assert_called_once_with(expected_output_dto)
