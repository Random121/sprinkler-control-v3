import json
import logging
import uuid
from jsonschema import exceptions, Validator
from jsonschema.validators import validator_for
from pymongo.collection import Collection

from .scheduler import Scheduler


class SchedulerManager:
    def __init__(self, scheduler: Scheduler, schedules_collection: Collection) -> None:
        self.scheduler = scheduler
        self.schedules = schedules_collection

        with open("schemas/schedule.schema.json") as schema:
            SCHEDULE_SCHEMA = json.load(schema)

        self.validate_schedule = self._build_schedule_validator(SCHEDULE_SCHEMA)

    # slightly more optimized jsonschema validator which doesn't recreate
    # the validator class every function call
    def _build_schedule_validator(self, schema: dict, *args, **kwargs):
        _validator_class: Validator = validator_for(schema=schema)
        _validator_class.check_schema(schema=schema)
        _validator: Validator = _validator_class(schema, *args, **kwargs)

        def validator(instance):
            error = exceptions.best_match(_validator.iter_errors(instance))
            if error is not None:
                raise error

        return validator

    def _get_active_state(self, schedule: dict):
        return (schedule is not None) and schedule.get("active", False)

    def add_schedule(self, schedule: dict):
        # validate schedule using json schema
        self.validate_schedule(schedule)

        schedule["_id"] = str(uuid.uuid4())
        self.schedules.insert_one(schedule)

    def update_schedule(self, id: str, new_schedule: dict):
        # validate schedule using json schema
        self.validate_schedule(new_schedule)

        before: dict = self.schedules.find_one_and_replace({"_id": id}, new_schedule)

        # only need to update if the schedule was active
        if self._get_active_state(before):
            self.scheduler.update()

    def remove_schedule(self, id: str):
        deleted: dict = self.schedules.find_one_and_delete({"_id": id})

        # only need to update if the schedule was active
        if self._get_active_state(deleted):
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
        return self._get_active_state(schedule)

    def get_active(self):
        return self.schedules.find_one({"active": True})

    def start(self):
        logging.info("Scheduler manager is starting")
        self.scheduler.start()

    def stop(self):
        logging.info("Scheduler manager is stopping")
        self.scheduler.stop()
