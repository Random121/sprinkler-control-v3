from flask_restful import abort, Resource, reqparse, request as flask_request
from jsonschema import ValidationError

from .utils import get_schema_error_message
from models.Scheduler.manager import ScheduleManager


class ScheduleAPI(Resource):
    def __init__(self, schedule_manager: ScheduleManager) -> None:
        self.manager = schedule_manager

    def _abort_if_invalid_schedule(self, schedule_id: str):
        if not self.manager.is_schedule(schedule_id):
            abort(422, message=f"No schedule found with identifier {schedule_id}")

    def get(self, schedule_id: str):
        self._abort_if_invalid_schedule(schedule_id)
        return self.manager.get_schedules({"_id": schedule_id})

    def delete(self, schedule_id: str):
        self._abort_if_invalid_schedule(schedule_id)
        self.manager.remove_schedule(schedule_id)

    def put(self, schedule_id: str):
        self._abort_if_invalid_schedule(schedule_id)

        schedule: dict = flask_request.get_json()

        try:
            self.manager.update_schedule(schedule_id, schedule)
        except ValidationError as error:
            abort(400, message=get_schema_error_message(error))


class ScheduleListAPI(Resource):
    def __init__(self, schedule_manager: ScheduleManager) -> None:
        self.manager = schedule_manager

    def get(self):
        return self.manager.get_schedules()

    def post(self):
        schedule: dict = flask_request.get_json()

        try:
            self.manager.add_schedule(schedule)
        except ValidationError as error:
            abort(400, message=get_schema_error_message(error))


class ActiveScheduleAPI(Resource):
    def __init__(self, schedule_manager: ScheduleManager) -> None:
        self.manager = schedule_manager

    def _abort_if_invalid_schedule(self, schedule_id: str):
        if not self.manager.is_schedule(schedule_id):
            abort(422, message=f"No schedule found with identifier {schedule_id}")

    def get(self, schedule_id: (str | None) = None):
        return self.manager.get_active()

    def put(self, schedule_id: str):
        self._abort_if_invalid_schedule(schedule_id)
        self.manager.set_active(schedule_id, True)

    def delete(self, schedule_id: str):
        self._abort_if_invalid_schedule(schedule_id)
        self.manager.set_active(schedule_id, False)
