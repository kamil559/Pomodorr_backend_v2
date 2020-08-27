from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from pomodoros.application.repositories.date_frames import DateFramesRepository
from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.domain.entities import DateFrame
from pomodoros.domain.validations.date_frame_validations import check_for_colliding_date_frames
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

    def execute(self, input_dto: StartPomodoroInputDto) -> None:
        task = self.tasks_repository.get(task_id=input_dto.task_id)
        check_for_colliding_date_frames(task=task, start_date=input_dto.start_date, end_date=None)

        new_date_frame = DateFrame(
            id=None,
            start=input_dto.start_date,
            end=None,
            frame_type=input_dto.frame_type,
            task_id=input_dto.task_id
        )
        self.date_frames_repository.save(new_date_frame)

        output_dto = StartPomodoroOutputDto(
            id=new_date_frame.id,
            start_date=new_date_frame.start,
            frame_type=new_date_frame.frame_type
        )
        self.output_boundary.present(output_dto=output_dto)
