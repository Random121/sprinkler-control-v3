import logging
import dateutil.parser
from pymongo.collection import Collection
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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
            # seconds is optional
            "start_time": "1:00",
            # enable duration in seconds
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
        {"start_time": "10:06", "duration": 30, "relay_id": "GPIO_19"},
    ],
}


class Scheduler:
    def __init__(
        self,
        relay_board: RelayBoard,
        db_schedules_collection: Collection,
    ) -> None:
        self.scheduler = BackgroundScheduler(daemon=True)
        self.board = relay_board
        self.schedules_collection = db_schedules_collection

    def get_active_schedule(self) -> dict:
        return self.schedules_collection.find_one({"active": True}, max_time_ms=1000)

    def update_jobs(self):
        active_schedule = self.get_active_schedule()

        # disable scheduler since there is no active schedules
        if active_schedule is None:
            self.scheduler.pause()
            self.reset()
            return

        schedule_name = active_schedule.get("name")
        schedule_days = active_schedule.get("days")
        schedule_tasks = active_schedule.get("tasks")

        if active_schedule is None:
            raise Exception("Scheduler update_jobs() is called without setting an active schedule")

        if schedule_days is None:
            raise Exception("Schedule days were not specified")

        if schedule_tasks is None:
            raise Exception(f"No tasks were specified for schedule: {schedule_name}")

        logging.info(f"Updating jobs for schedule: {schedule_name}")

        self.scheduler.pause()
        self.reset()

        # assume user specified every day of the week if there are 7 active days
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
                second=start_time.second,
            )

            self.scheduler.add_job(
                self.board.enable,
                trigger=task_trigger,
                args=[task.get("relay_id"), task.get("duration")],
                misfire_grace_time=1,
                coalesce=True,
            )

            logging.info(f"Added task with trigger {task_trigger}")

        self.scheduler.resume()

    def reset(self):
        self.scheduler.remove_all_jobs()
        self.board.disable()

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.board.disable()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            self.update_jobs()
