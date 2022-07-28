from flask_restful import abort, Resource

from sprinkler_server.models.Scheduler import ScheduleManager


class ActiveScheduleAPI(Resource):
    def __init__(self, schedule_manager: ScheduleManager) -> None:
        self.manager = schedule_manager

    def _abort_if_invalid_schedule(self, schedule_id: str):
        if not self.manager.is_schedule(schedule_id):
            abort(422, message=f"No schedule found with identifier {schedule_id}")

    def get(self, schedule_id = None):
        return self.manager.get_active()

    def put(self, schedule_id: str):
        self._abort_if_invalid_schedule(schedule_id)
        self.manager.set_active(schedule_id, True)

    def delete(self, schedule_id: str):
        self._abort_if_invalid_schedule(schedule_id)
        self.manager.set_active(schedule_id, False)
