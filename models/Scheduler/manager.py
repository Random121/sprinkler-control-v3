import logging
import uuid
import fastjsonschema
from pymongo.collection import Collection

from .scheduler import Scheduler

SCHEDULE_SCHEMA = {
    "title": "Schedule",
    "description": "A schedule which can be interpreted by the scheduler",
    "type": "object",
    "properties": {
        "name": {
            "description": "A non-unique display name",
            "type": "string",
        },
        "days": {
            "description": "Days of week which the schedule will run",
            "type": "array",
            "items": {
                "type": "integer",
                "minimum": 0,
                "maximum": 6,
            },
            "minItems": 1,
            "maxItems": 7,
            "uniqueItems": True,
        },
        "tasks": {
            "description": "Tasks to be run in the schedule",
            "type": "array",
            "items": {
                "description": "A task to enable a relay for a specific time",
                "type": "object",
                "properties": {
                    "start": {
                        "description": "Time to start the relay",
                        "type": "string",
                        # modification of https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s06.html
                        "pattern": "^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])(:([0-5]?[0-9]))?$",
                    },
                    "duration": {
                        "description": "Duration to enable relay for",
                        "type": "integer",
                        "minimum": 1,
                    },
                    "id": {
                        "description": "Identifier of relay to enable",
                        "type": "string",
                    }
                },
                "required": ["start", "duration", "id"],
                "additionalProperties": False,
            },
            "minItems": 1,
        },
    },
    "required": ["name", "days", "tasks"],
    "additionalProperties": False,
}

class SchedulerManager:
    def __init__(self, scheduler: Scheduler, schedules_collection: Collection) -> None:
        self.scheduler = scheduler
        self.schedules = schedules_collection
        self.validate_schedule = fastjsonschema.compile(SCHEDULE_SCHEMA)

    # TODO: do schedule validation here
    # client can't specify the "active" and "_id" fields
    def add_schedule(self, schedule: dict, set_active: bool):
        # validate schedule using json schema
        self.validate_schedule(schedule)

        random_id = str(uuid.uuid4())
        schedule["_id"] = random_id

        self.schedules.insert_one(schedule)

        if set_active:
            self.set_active(random_id)

    def remove_schedule(self, id: str):
        deleted: dict = self.schedules.find_one_and_delete({"_id": id})

        # only update if the schedule deleted was active
        should_update = (deleted is not None) and deleted.get("active", False)

        if should_update:
            self.scheduler.update()

    # @param filter mongodb filter which is optional
    def get_schedules(self, filter: str = None):
        filter = {} if filter is None else filter
        return list(self.schedules.find(filter))

    def is_schedule(self, id: str):
        count = self.schedules.count_documents({"_id": id}, limit=1)
        return count > 0

    # sets the specified scheduler as active
    # disables the previous active schedule (only one active schedule exists)
    def set_active(self, id: str):
        result = self.schedules.update_one({"_id": id}, {"$set": {"active": True}})

        # exclude cases where the schedule is already active
        if result.modified_count > 0:
            disable_filter = {"_id": {"$ne": id}, "active": True}
            self.schedules.update_one(disable_filter, {"$set": {"active": False}})
            self.scheduler.update()

    # check if a schedule is active
    def is_active(self, id: str):
        schedule: dict = self.schedules.find_one({"_id": id})
        return (schedule is not None) and schedule.get("active", False)

    def get_active(self):
        return self.schedules.find_one({"active": True})

    def start(self):
        logging.info("Scheduler manager is starting")
        self.scheduler.start()

    def stop(self):
        logging.info("Scheduler manager is stopping")
        self.scheduler.stop()