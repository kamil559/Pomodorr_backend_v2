import http

from flask import jsonify, make_response
from pomodoros import (
    CompleteTaskOutputDto,
    PausePomodoroOutputBoundary,
    PinTaskToProjectOutputBoundary,
    PinTaskToProjectOutputDto,
    ReactivateTaskOutputBoundary,
    ReactivateTaskOutputDto,
)
from web_app.marshallers.tasks import CompleteTaskSchema, PinTaskToProjectSchema, ReactivateTaskSchema


class JSONCompleteTaskOutputBoundary(PausePomodoroOutputBoundary):
    def present(self, output_dto: CompleteTaskOutputDto) -> None:
        serialized_output_data = CompleteTaskSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), http.HTTPStatus.OK)


class JSONReactivateTaskPresenter(ReactivateTaskOutputBoundary):
    def present(self, output_dto: ReactivateTaskOutputDto) -> None:
        serialized_output_data = ReactivateTaskSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), http.HTTPStatus.OK)


class JSONPinTaskToProjectPresenter(PinTaskToProjectOutputBoundary):
    def present(self, output_dto: PinTaskToProjectOutputDto) -> None:
        serialized_output_data = PinTaskToProjectSchema().dump(output_dto)
        self.response = make_response(jsonify(serialized_output_data), http.HTTPStatus.OK)
