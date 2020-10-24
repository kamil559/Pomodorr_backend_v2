from dataclasses import dataclass
from datetime import datetime
from gettext import gettext as _
from typing import List, Optional

from foundation.value_objects import DateFrameDefinition, Priority
from pomodoros.domain.entities import SubTask
from pomodoros.domain.exceptions import (
    NoActionAllowedOnCompletedTask,
    TaskAlreadyActive,
    TaskAlreadyCompleted,
    TaskNameNotAvailableInNewProject,
)
from pomodoros.domain.value_objects import Ordering, PomodoroRenewalInterval, ProjectId, TaskId, TaskStatus


@dataclass
class Task:
    id: TaskId
    project_id: ProjectId
    name: str
    status: TaskStatus
    priority: Priority
    ordering: Ordering
    due_date: Optional[datetime]
    pomodoros_to_do: int
    pomodoros_burn_down: int
    date_frame_definition: Optional[DateFrameDefinition]
    reminder_date: Optional[datetime]
    renewal_interval: Optional[PomodoroRenewalInterval]
    note: Optional[str]
    created_at: datetime
    sub_tasks: Optional[List[SubTask]]

    @property
    def next_due_date(self) -> datetime:
        return self.due_date + self.renewal_interval

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED

    @property
    def is_repeatable(self) -> bool:
        return self.renewal_interval is not None

    @property
    def is_active(self) -> bool:
        return self.status == TaskStatus.ACTIVE

    def check_can_perform_actions(self) -> None:
        if self.is_completed:
            raise NoActionAllowedOnCompletedTask(
                _("pomodoros.domain.entities.task.no_action_allowed_on_completed_task")
            )

    def _check_already_active(self) -> None:
        if self.is_active:
            raise TaskAlreadyActive(_("pomodoros.domain.entities.task.task_already_active"))

    def _check_already_completed(self) -> None:
        if self.is_completed:
            raise TaskAlreadyCompleted(_("pomodoros.domain.entities.task.task_"))

    def _check_task_name_available_in_project(self, project_tasks: Optional[List["Task"]]) -> None:
        task_in_new_project = list(filter(lambda task: task.is_active and task.name == self.name, project_tasks))

        if len(task_in_new_project):
            raise TaskNameNotAvailableInNewProject(
                _("pomodoros.domain.entities.task.task_name_not_available_in_new_project")
            )

    def complete(self) -> None:
        self._check_already_completed()
        self.status = TaskStatus.COMPLETED

    def pin_to_new_project(self, new_project_id: ProjectId, new_project_tasks: Optional[List["Task"]]) -> None:
        self.check_can_perform_actions()
        self._check_task_name_available_in_project(new_project_tasks)

        self.project_id = new_project_id

    def reactivate(self, project_tasks: Optional[List["Task"]]) -> None:
        self._check_already_active()
        self._check_task_name_available_in_project(project_tasks)

        self.status = TaskStatus.ACTIVE

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self.__dict__ == other.__dict__
