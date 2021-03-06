import http

from flask import jsonify
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
from web_app.marshallers.pomodoros import (
    BeginPomodoroSchema,
    FinishPomodoroSchema,
    PausePomodoroSchema,
    ResumePomodoroSchema,
)


class JSONBeginPomodoroPresenter(BeginPomodoroOutputBoundary):
    def present(self, output_dto: BeginPomodoroOutputDto) -> None:
        serialized_output_data = BeginPomodoroSchema().dump(output_dto)
        self.response = jsonify(serialized_output_data), http.HTTPStatus.CREATED


class JSONPausePomodoroPresenter(PausePomodoroOutputBoundary):
    def present(self, output_dto: PausePomodoroOutputDto) -> None:
        serialized_output_data = PausePomodoroSchema().dump(output_dto)
        self.response = jsonify(serialized_output_data), http.HTTPStatus.OK


class JSONResumePomodoroPresenter(ResumePomodoroOutputBoundary):
    def present(self, output_dto: ResumePomodoroOutputDto) -> None:
        serialized_output_data = ResumePomodoroSchema().dump(output_dto)
        self.response = jsonify(serialized_output_data), http.HTTPStatus.OK


class JSONFinishPomodoroPresenter(FinishPomodoroOutputBoundary):
    def present(self, output_dto: FinishPomodoroOutputDto) -> None:
        serialized_output_data = FinishPomodoroSchema().dump(output_dto)
        self.response = jsonify(serialized_output_data), http.HTTPStatus.OK
