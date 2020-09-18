import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from pomodoros.application.repositories.pauses import PausesRepository
from pomodoros.application.repositories.pomodoros import PomodorosRepository
from pomodoros.domain.entities.pause import Pause
from pomodoros.domain.entities.pomodoro import Pomodoro
from pomodoros.domain.value_objects import DateFrameId, FrameType


@dataclass
class BeginPauseInputDto:
    pomodoro_id: DateFrameId
    start_date: datetime
    frame_type: FrameType


@dataclass
class BeginPauseOutputDto:
    id: DateFrameId
    pomodoro_id: DateFrameId
    start_date: datetime
    frame_type: FrameType


class BeginPauseOutputBoundary(ABC):
    @abstractmethod
    def present(self, output_dto: BeginPauseOutputDto) -> None:
        pass


class BeginPause:
    def __init__(self, output_boundary: BeginPauseOutputBoundary, pomodoros_repository: PomodorosRepository,
                 pauses_repository: PausesRepository):
        self.output_boundary = output_boundary
        self.pomodoros_repository = pomodoros_repository
        self.pauses_repository = pauses_repository

    @staticmethod
    def _produce_pause(frame_type: FrameType, pomodoro: Pomodoro) -> Pause:
        return Pause(id=uuid.uuid4(), frame_type=frame_type, start_date=None, end_date=None, pomodoro=pomodoro)

    def execute(self, input_dto: BeginPauseInputDto) -> None:
        pomodoro = self.pomodoros_repository.get(pomodoro_id=input_dto.pomodoro_id)

        new_pause = self._produce_pause(frame_type=input_dto.frame_type, pomodoro=pomodoro)
        new_pause.begin(start_date=input_dto.start_date)
        self.pauses_repository.save(new_pause)

        output_dto = BeginPauseOutputDto(
            id=new_pause.id,
            pomodoro_id=pomodoro.id,
            frame_type=new_pause.frame_type,
            start_date=new_pause.start_date
        )

        self.output_boundary.present(output_dto=output_dto)
