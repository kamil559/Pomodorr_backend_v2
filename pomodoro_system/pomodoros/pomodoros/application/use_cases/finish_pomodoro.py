from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from pomodoros.application.repositories.date_frames import DateFramesRepository
from pomodoros.domain.exceptions import PomodoroErrorMarginExceeded
from pomodoros.domain.validations.pomodoro_validations import check_for_colliding_pomodoros, check_pomodoro_length
from pomodoros.domain.value_objects import DateFrameId, FrameType


@dataclass
class FinishPomodoroInputDto:
    id: DateFrameId
    end_date: datetime


@dataclass
class FinishPomodoroOutputDto:
    id: DateFrameId
    start_date: datetime
    end_date: datetime
    frame_type: FrameType


@dataclass
class FinishPomodoroOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: FinishPomodoroOutputDto):
        pass


class FinishPomodoro:
    def __init__(self, output_boundary: FinishPomodoroOutputBoundary, date_frames_repository: DateFramesRepository):
        self.output_boundary = output_boundary
        self.date_frames_repository = date_frames_repository

    def execute(self, input_dto: FinishPomodoroInputDto) -> None:
        pomodoro = self.date_frames_repository.get(date_frame_id=input_dto.id)
        task = pomodoro.task

        try:
            check_pomodoro_length(pomodoro=pomodoro, end_date=input_dto.end_date)
        except PomodoroErrorMarginExceeded:
            self._automatic_end_date_fix(pomodoro=pomodoro)

        check_for_colliding_pomodoros(task=task, start_date=pomodoro.start_date, end_date=input_dto.end_date,
                                      excluded_date_frame_ids={pomodoro.id})

        pomodoro.finish(end_date=input_dto.end_date)
        self.date_frames_repository.save(pomodoro)

        output_dto = FinishPomodoroOutputDto(id=pomodoro.id, start_date=pomodoro.start_date, end_date=pomodoro.end_date,
                                             frame_type=pomodoro.frame_type)
        self.output_boundary.present(output_dto=output_dto)
