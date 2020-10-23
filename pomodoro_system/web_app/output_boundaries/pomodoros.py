from flask import make_response, jsonify

from pomodoros import (BeginPomodoroOutputBoundary, BeginPomodoroOutputDto, PausePomodoroOutputBoundary,
                       PausePomodoroOutputDto, ResumePomodoroOutputBoundary, ResumePomodoroOutputDto,
                       FinishPomodoroOutputBoundary, FinishPomodoroOutputDto, CompleteTaskOutputBoundary,
                       CompleteTaskOutputDto, ReactivateTaskOutputBoundary, ReactivateTaskOutputDto,
                       PinTaskToProjectOutputBoundary, PinTaskToProjectOutputDto)
from serializers.pomodoros import BeginPomodoroSchema, PausePomodoroSchema, ResumePomodoroSchema, FinishPomodoroSchema


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


class JSONCompleteTaskPresenter(CompleteTaskOutputBoundary):
    def present(self, output_dto: CompleteTaskOutputDto) -> None:
        pass


class JSONReactivateTaskPresenter(ReactivateTaskOutputBoundary):
    def present(self, output_dto: ReactivateTaskOutputDto) -> None:
        pass


class JSONPinTaskToProjectPresenter(PinTaskToProjectOutputBoundary):
    def present(self, output_dto: PinTaskToProjectOutputDto) -> None:
        pass
