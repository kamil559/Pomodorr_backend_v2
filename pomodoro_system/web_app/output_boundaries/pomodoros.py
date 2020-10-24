from flask import jsonify, make_response

from pomodoros import (
    BeginPomodoroOutputBoundary,
    BeginPomodoroOutputDto,
    FinishPomodoroOutputBoundary,
    FinishPomodoroOutputDto,
    PausePomodoroOutputBoundary,
    PausePomodoroOutputDto,
    ResumePomodoroOutputBoundary,
    ResumePomodoroOutputDto,
)
from web_app.serializers.pomodoros import (
    BeginPomodoroSchema,
    FinishPomodoroSchema,
    PausePomodoroSchema,
    ResumePomodoroSchema,
)


class JSONBeginPomodoroPresenter(BeginPomodoroOutputBoundary):
    def present(self, output_dto: BeginPomodoroOutputDto) -> None:
        serialized_output_data = BeginPomodoroSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), 201)


class JSONPausePomodoroPresenter(PausePomodoroOutputBoundary):
    def present(self, output_dto: PausePomodoroOutputDto) -> None:
        serialized_output_data = PausePomodoroSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), 200)


class JSONResumePomodoroPresenter(ResumePomodoroOutputBoundary):
    def present(self, output_dto: ResumePomodoroOutputDto) -> None:
        serialized_output_data = ResumePomodoroSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), 200)


class JSONFinishPomodoroPresenter(FinishPomodoroOutputBoundary):
    def present(self, output_dto: FinishPomodoroOutputDto) -> None:
        serialized_output_data = FinishPomodoroSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), 200)
