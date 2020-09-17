from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from pomodoros.application.repositories.pauses import PausesRepository
from pomodoros.domain.value_objects import DateFrameId, FrameType


@dataclass
class FinishPauseInputDto:
    pause_id: DateFrameId
    end_date: datetime


@dataclass
class FinishPauseOutputDto:
    id: DateFrameId
    pomodoro_id: DateFrameId
    start_date: datetime
    end_date: datetime
    frame_type: FrameType


class FinishPauseOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: FinishPauseOutputDto) -> None:
        pass


class FinishPause:
    def __init__(self, output_boundary: FinishPauseOutputBoundary, pauses_repository: PausesRepository) -> None:
        self.output_boundary = output_boundary
        self.pauses_repository = pauses_repository

    def execute(self, input_dto: FinishPauseInputDto) -> None:
        pause = self.pauses_repository.get(pause_id=input_dto.pause_id)

        pause.finish(end_date=input_dto.end_date)
        self.pauses_repository.save(pause)

        output_dto = FinishPauseOutputDto(id=pause.id, pomodoro_id=pause.pomodoro.id, start_date=pause.start_date,
                                          end_date=pause.end_date, frame_type=pause.frame_type)

        self.output_boundary.present(output_dto=output_dto)
