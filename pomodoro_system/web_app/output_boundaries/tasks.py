from flask import make_response, jsonify

from pomodoros import PausePomodoroOutputBoundary, PausePomodoroOutputDto
from serializers.tasks import CompleteTaskSchema


class JSONPausePomodoroOutputBoundary(PausePomodoroOutputBoundary):
    def present(self, output_dto: PausePomodoroOutputDto) -> None:
        serialized_output_data = CompleteTaskSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), 200)
