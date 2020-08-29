from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from pomodoros.application.repositories.date_frames import DateFramesRepository
from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.domain.entities import DateFrame, Task
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.validations.pomodoro_validations import check_for_colliding_pomodoros
from pomodoros.domain.value_objects import FrameType, DateFrameId, TaskId


@dataclass
class StartPomodoroInputDto:
    start_date: datetime
    frame_type: FrameType
    task_id: TaskId


@dataclass
class StartPomodoroOutputDto:
    id: DateFrameId
    start_date: datetime
    frame_type: FrameType


@dataclass
class StartPomodoroOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: StartPomodoroOutputDto):
        pass


class StartPomodoro:
    def __init__(self, output_boundary: StartPomodoroOutputBoundary, date_frames_repository: DateFramesRepository,
                 tasks_repository: TasksRepository):
        self.output_boundary = output_boundary
        self.date_frames_repository = date_frames_repository
        self.tasks_repository = tasks_repository

    @staticmethod
    def _produce_pomodoro(frame_type: FrameType, task: Task) -> DateFrame:
        if frame_type == FrameType.TYPE_POMODORO:
            return Pomodoro(id=None, frame_type=FrameType.TYPE_POMODORO, start_date=None, end_date=None, task=task,
                            contained_pauses=None)

    def execute(self, input_dto: StartPomodoroInputDto) -> None:
        task = self.tasks_repository.get(task_id=input_dto.task_id)
        check_for_colliding_pomodoros(task=task, start_date=input_dto.start_date, end_date=None)

        new_pomodoro = self._produce_pomodoro(frame_type=input_dto.frame_type, task=task)

        new_pomodoro.start(start_date=input_dto.start_date)
        self.date_frames_repository.save(new_pomodoro)

        output_dto = StartPomodoroOutputDto(
            id=new_pomodoro.id,
            start_date=new_pomodoro.start_date,
            frame_type=new_pomodoro.frame_type
        )
        self.output_boundary.present(output_dto=output_dto)
