from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from pomodoros.application.repositories.date_frames import DateFramesRepository
from pomodoros.domain.validations.date_frame_validations import check_for_colliding_date_frames
from pomodoros.domain.value_objects import DateFrameId, FrameType


@dataclass
class FinishDateFrameInputDto:
    id: DateFrameId
    end_date: datetime


@dataclass
class FinishDateFrameOutputDto:
    id: DateFrameId
    start_date: datetime
    end_date: datetime
    frame_type: FrameType


@dataclass
class FinishDateFrameOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: FinishDateFrameOutputDto):
        pass


class FinishDateFrame:
    def __init__(self, output_boundary: FinishDateFrameOutputBoundary, date_frames_repository: DateFramesRepository):
        self.output_boundary = output_boundary
        self.date_frames_repository = date_frames_repository

    def execute(self, input_dto: FinishDateFrameInputDto) -> None:
        date_frame = self.date_frames_repository.get(date_frame_id=input_dto.id)
        task = date_frame.task
        check_for_colliding_date_frames(task=task, start_date=date_frame.start, end_date=input_dto.end_date,
                                        excluded_date_frame_ids=[date_frame.id])

        date_frame.finish_date_frame(end_date=input_dto.end_date)
        self.date_frames_repository.save(date_frame)

        output_dto = FinishDateFrameOutputDto(id=date_frame.id, start_date=date_frame.start, end_date=date_frame.end,
                                              frame_type=date_frame.frame_type)
        self.output_boundary.present(output_dto=output_dto)
