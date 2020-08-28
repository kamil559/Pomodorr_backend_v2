from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from pomodoros.application.repositories.date_frames import DateFramesRepository
from pomodoros.application.repositories.tasks import TasksRepository
from pomodoros.domain.entities import DateFrame
from pomodoros.domain.validations.date_frame_validations import check_for_colliding_date_frames
from pomodoros.domain.value_objects import FrameType, DateFrameId, TaskId


@dataclass
class StartDateFrameInputDto:
    start_date: datetime
    frame_type: FrameType
    task_id: TaskId


@dataclass
class StartDateFrameOutputDto:
    id: DateFrameId
    start_date: datetime
    frame_type: FrameType


@dataclass
class StartDateFrameOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: StartDateFrameOutputDto):
        pass


class StartDateFrame:
    def __init__(self, output_boundary: StartDateFrameOutputBoundary, date_frames_repository: DateFramesRepository,
                 tasks_repository: TasksRepository):
        self.output_boundary = output_boundary
        self.date_frames_repository = date_frames_repository
        self.tasks_repository = tasks_repository

    def execute(self, input_dto: StartDateFrameInputDto) -> None:
        task = self.tasks_repository.get(task_id=input_dto.task_id)
        check_for_colliding_date_frames(task=task, start_date=input_dto.start_date, end_date=None)

        new_date_frame = DateFrame(
            id=None,
            frame_type=input_dto.frame_type,
            task=task
        )

        new_date_frame.start_date_frame(start_date=input_dto.start_date)
        self.date_frames_repository.save(new_date_frame)

        output_dto = StartDateFrameOutputDto(
            id=new_date_frame.id,
            start_date=new_date_frame.start,
            frame_type=new_date_frame.frame_type
        )
        self.output_boundary.present(output_dto=output_dto)
