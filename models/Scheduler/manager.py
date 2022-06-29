import logging
import eventlet
from pymongo.collection import Collection

from .scheduler import Scheduler

SCHEDULE_ENABLE_UPDATE = {
    "$set": {
        "active": True,
    }
}

SCHEDULE_DISABLE_UPDATE = {
    "$set": {
        "active": False,
    }
}


class SchedulerManager:
    def __init__(
        self,
        scheduler: Scheduler,
        db_schedules_collection: Collection,
    ) -> None:
        self.scheduler = scheduler
        self.schedules_collection = db_schedules_collection

    def add_schedule(self, schedule: dict):
        self.schedules_collection.insert_one(schedule)

    def remove_schedule(self, id: str):
        self.schedules_collection.delete_many({"name": id})
        self.scheduler.update_jobs()

    # TODO: implement a proper ID that is not the schedule name
    # setting ID to none or empty disables all active schedules
    def set_schedule_active_state(self, id: str, state: bool):
        # disable all active schedules
        self.schedules_collection.update_many({"active": True}, SCHEDULE_DISABLE_UPDATE)

        # set the specified schedule to active
        self.schedules_collection.update_one(
            {"name": id},
            SCHEDULE_ENABLE_UPDATE if state else SCHEDULE_DISABLE_UPDATE,
        )

        self.scheduler.update_jobs()

    def get_active_schedule(self):
        return self.schedules_collection.find_one({"active": True})

    def get_all_schedules(self):
        return list(self.schedules_collection.find({}))

    def is_schedule(self, filter: dict):
        return self.schedules_collection.find_one(filter) is not None

    def stop(self):
        logging.info("Scheduler manager is stopping")
        self.scheduler.stop()

    def start(self):
        logging.info("Scheduler manager is starting")
        self.scheduler.start()
