from pomodoros.application.use_cases.pin_task_to_project import (
    PinTaskToProjectInputDto, PinTaskToProjectOutputDto)
from pomodoros.tests.factories import ProjectFactory


def test_pin_task_to_project_use_case(task, pin_task_to_project_output_boundary, pin_task_to_project_use_case):
    new_project = ProjectFactory()

    pin_to_project_input_dto = PinTaskToProjectInputDto(id=task.id, new_project_id=new_project.id)

    pin_task_to_project_use_case.execute(input_dto=pin_to_project_input_dto)

    expected_output_dto = PinTaskToProjectOutputDto(id=task.id, new_project_id=new_project.id)

    assert task.project_id == new_project.id
    pin_task_to_project_output_boundary.present.assert_called_once_with(expected_output_dto)
