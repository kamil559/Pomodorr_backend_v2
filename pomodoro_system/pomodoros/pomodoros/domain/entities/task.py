from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from foundation.value_objects import DateFrameDefinition, Priority
from pomodoros.domain.entities import SubTask, Project
from pomodoros.domain.exceptions import (
    TaskNameNotAvailableInNewProject, NoActionAllowedOnCompletedTask, TaskAlreadyActive)
from pomodoros.domain.value_objects import TaskStatus, Ordering, PomodoroRenewalInterval, TaskId, ProjectId


@dataclass
class Task:
    id: TaskId
    project_id: ProjectId
    name: str
    status: TaskStatus
    priority: Priority
    ordering: Ordering
    due_date: datetime
    pomodoros_to_do: int
    pomodoros_burn_down: int
    date_frame_definition: Optional[DateFrameDefinition]
    reminder_date: datetime
    renewal_interval: PomodoroRenewalInterval
    note: str
    created_at: datetime
    sub_tasks: Optional[List[SubTask]]

    @property
    def next_due_date(self) -> datetime:
        return self.due_date + self.renewal_interval

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED

    @property
    def is_active(self) -> bool:
        return self.status == TaskStatus.ACTIVE

    def check_can_perform_actions(self) -> None:
        if self.is_completed:
            raise NoActionAllowedOnCompletedTask

    def check_already_active(self) -> None:
        if self.is_active:
            raise TaskAlreadyActive

    def _check_task_name_available_in_project(self, project: Project) -> None:
        task_in_new_project = list(
            filter(lambda task: task.status == TaskStatus.ACTIVE and task.name == self.name, project.tasks))

        if len(task_in_new_project):
            raise TaskNameNotAvailableInNewProject

    def pin_to_new_project(self, new_project: Project) -> None:
        self.check_can_perform_actions()
        self._check_task_name_available_in_project(project=new_project)

        self.project = new_project

    def reactivate(self) -> None:
        self.check_can_perform_actions()
        self.check_already_active()
        self._check_task_name_available_in_project(project=self.project)

        self.status = TaskStatus.ACTIVE
