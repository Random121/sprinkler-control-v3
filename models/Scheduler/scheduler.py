import logging
import dateutil.parser
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# nice job pymongo
from pymongo import MongoClient
import eventlet
pymongo = eventlet.import_patched("pymongo")

from models.Relay.board import RelayBoard


SCHEDULE_FORMAT = {
    # TODO: implement unique IDs for schedules
    "name": "Schedule 1",
    # scheduler always runs the active schedule
    "active": True,
    # cron day of the week (0=sunday, 1=monday ... 6=saturday)
    "days": [0, 2, 5],
    "tasks": [
        {
            # 24 hour time (00:00 - 23:59)
            "start_time": "1:00",
            # enable duration in minutes
            "duration": 60,
            # id of relay to schedule for
            "relay_id": "GPIO_6",
        },
        {
            # NOTE: overlap between times should not matter
            # since the board doesn't allow two relays
            # enabled at the same time
            # NOTE: validating the time should
            # be a future addition
            "start_time": "2:00",
            "duration": 30,
            "relay_id": "GPIO_13",
        },
    ],
}

TEST_SCHEDULE = {
    "name": "Test schedule 1",
    "active": True,
    "days": [0, 2, 5],
    "tasks": [
        {"start_time": "1:00", "duration": 30, "relay_id": "GPIO_6"},
        {"start_time": "2:00", "duration": 60, "relay_id": "GPIO_13"},
        {"start_time": "4:30", "duration": 1, "relay_id": "GPIO_19"},
    ],
}


class Scheduler:
    def __init__(self, relay_board: RelayBoard) -> None:
        self.scheduler = BackgroundScheduler(daemon=True)
        self.board = relay_board

    def get_active_schedule(self) -> dict:
        mongo_client: MongoClient = pymongo.MongoClient("mongodb+srv://user:user@cluster0.di3hb.mongodb.net/?retryWrites=true&w=majority")
        sprinkler_control_db = mongo_client["sprinkler_control"]
        schedules_collection = sprinkler_control_db["schedules"]

        return schedules_collection.find_one({"active": True}, max_time_ms=1000)

    def update_jobs(self):
        self.scheduler.pause()
        self.scheduler.remove_all_jobs()
        self.board.disable()

        active_schedule = self.get_active_schedule()
        schedule_name = active_schedule.get("name", "No name was provided")
        schedule_days = active_schedule.get("days")
        schedule_tasks = active_schedule.get("tasks")

        if active_schedule is None:
            raise Exception("Scheduler update_jobs() is called without setting an active schedule")

        if schedule_days is None:
            raise Exception("Schedule days were not specified")

        if schedule_tasks is None:
            raise Exception(f"No tasks were specified for schedule: {schedule_name}")

        logging.info(f"Updating jobs for schedule: {schedule_name}")

        # assume user specified every day of the week if there is 7 active days
        cron_day_of_week = (
            "*"
            if len(schedule_days) == 7
            else (",").join(str(day) for day in schedule_days)
        )

        task: dict
        for task in schedule_tasks:
            start_time = dateutil.parser.parse(task.get("start_time"))
            task_trigger = CronTrigger(
                day_of_week=cron_day_of_week,
                hour=start_time.hour,
                minute=start_time.minute,
            )

            self.scheduler.add_job(
                self.board.enable,
                trigger=task_trigger,
                args=[task.get("relay_id"), task.get("duration")],
                misfire_grace_time=1,
                coalesce=True,
            )

            logging.info(f"Added task trigger {task_trigger}")

        self.scheduler.resume()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.board.disable()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            self.update_jobs()
