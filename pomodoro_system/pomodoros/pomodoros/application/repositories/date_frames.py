from abc import abstractmethod, ABC

from pomodoros.domain.entities import DateFrame
from pomodoros.domain.value_objects import DateFrameId


class DateFramesRepository(ABC):
    @abstractmethod
    def get(self, date_frame_id: DateFrameId) -> DateFrame:
        pass

    @abstractmethod
    def save(self, date_frame: DateFrame) -> None:
        pass
