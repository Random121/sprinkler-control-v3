import logging
import uuid
from pymongo.collection import Collection

from .scheduler import Scheduler
from sprinkler_server.utils import build_jsonschema_validator


class ScheduleManager:
    def __init__(
        self,
        scheduler: Scheduler,
        schedules_collection: Collection,
        schedule_schema: dict,
    ) -> None:
        self.scheduler = scheduler
        self.schedules = schedules_collection
        self.validate_schedule = build_jsonschema_validator(schedule_schema)

    def _is_active(self, schedule: dict):
        return (schedule is not None) and schedule.get("active", False)

    def _preprocessor(self, schedule: dict):
        # add optional fields
        if "active" not in schedule:
            schedule["active"] = False

        # validate schedule using json schema
        self.validate_schedule(schedule)

    def _disable_schedules(self, exclude_id: str):
        disable_filter = {"_id": {"$ne": exclude_id}, "active": True}
        self.schedules.update_one(disable_filter, {"$set": {"active": False}})

    def add_schedule(self, schedule: dict):
        self._preprocessor(schedule)

        id = str(uuid.uuid4())
        schedule["_id"] = id

        self.schedules.insert_one(schedule)

        if self._is_active(schedule):
            self._disable_schedules(id)
            self.scheduler.update()

    def update_schedule(self, id: str, new_schedule: dict):
        self._preprocessor(new_schedule)

        before: dict = self.schedules.find_one_and_replace({"_id": id}, new_schedule)

        # only need to update if the schedule was active
        if self._is_active(new_schedule):
            self._disable_schedules(id)
            self.scheduler.update()

    def remove_schedule(self, id: str):
        deleted: dict = self.schedules.find_one_and_delete({"_id": id})

        # only need to update if the schedule was active
        if self._is_active(deleted):
            self.scheduler.update()

    # @param filter mongodb filter which is optional
    def get_schedules(self, filter: str = None):
        filter = {} if filter is None else filter
        return list(self.schedules.find(filter))

    def is_schedule(self, id: str):
        count = self.schedules.count_documents({"_id": id}, limit=1)
        return count > 0

    # set the active state of a schedule
    def set_active(self, id: str, active_state: bool):
        active_state = bool(active_state)

        result = self.schedules.update_one(
            {"_id": id},
            {"$set": {"active": bool(active_state)}},
        )

        # no need to update if nothing changed
        if result.modified_count > 0:

            # disable all other active schedules (max one active schedule)
            if active_state:
                self._disable_schedules(id)

            self.scheduler.update()

    # check if a schedule is active
    def is_active(self, id: str):
        schedule: dict = self.schedules.find_one({"_id": id})
        return self._is_active(schedule)

    def get_active(self):
        return self.schedules.find_one({"active": True})

    def start(self):
        logging.info("Scheduler manager is starting")
        self.scheduler.start()

    def stop(self):
        logging.info("Scheduler manager is stopping")
        self.scheduler.stop()
