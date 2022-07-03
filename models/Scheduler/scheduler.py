import logging
import dateutil.parser
from pymongo.collection import Collection
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from models.Relay import RelayBoard

SCHEDULE_FORMAT_V2 = {
    # unique ID for each schedule which is used internally
    "_id": "6b479aa3-c242-44f8-8751-956bf19b8fef",
    # non-unique user specified display name
    "name": "Schedule 1",
    # is this scheduler supposed to be ran
    "active": True,
    # days of week on which the schedules runs
    # cron format: 0=sunday, 1=monday ... 6=saturday
    "days": [0, 3, 6],
    # list of relays to be run, when and how long to run them for
    "tasks": [
        {
            # 24 hour time with seconds being optional (00:00 - 23:59)
            # time which the relay will be enabled
            "start": "1:00",
            # how long the relay should stay enabled (seconds)
            # TODO: check for time overlap in the future
            "duration": 60,
            # id to relay to enable
            "id": "GPIO_6",
        },
        {
            "start": "2:30:45",
            "duration": 120,
            "id": "GPIO_13",
        },
    ],
}

SCHEDULE_FORMAT_V1 = {
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
        {"start": "1:00", "duration": 30, "id": "GPIO_6"},
        {"start": "2:00", "duration": 60, "id": "GPIO_13"},
        {"start": "10:06", "duration": 30, "id": "GPIO_19"},
    ],
}


class Scheduler:
    def __init__(
        self,
        relay_board: RelayBoard,
        schedules_collection: Collection,
    ) -> None:
        self.scheduler = BackgroundScheduler(daemon=True)
        self.board = relay_board
        self.schedules = schedules_collection

    def fetch_active_schedule(self):
        logging.debug("Fetching active schedule")
        return self.schedules.find_one({"active": True}, max_time_ms=1000)

    def update_jobs(self, schedule: dict):
        schedule_id = schedule.get("_id")
        schedule_name = schedule.get("name")
        schedule_days = schedule.get("days")
        schedule_tasks = schedule.get("tasks")

        logging.info(f"Updating {len(schedule_tasks)} tasks for schedule {schedule_id} ({schedule_name})")

        self.scheduler.pause()
        self.reset()

        # assume user wants the schedule to be active for all days
        # if there are 7 specified days (total days in a week)
        cron_active_days = (
            "*"
            if len(schedule_days) == 7
            else (",").join(str(day) for day in schedule_days)
        )

        task: dict
        for task in schedule_tasks:
            start_time = dateutil.parser.parse(task.get("start"))
            task_trigger = CronTrigger(
                day_of_week=cron_active_days,
                hour=start_time.hour,
                minute=start_time.minute,
                second=start_time.second,
            )

            self.scheduler.add_job(
                self.board.enable,
                trigger=task_trigger,
                args=[task.get("id"), task.get("duration")],
                misfire_grace_time=1,
                coalesce=True,
            )

            logging.debug(f"Added job with trigger {task_trigger}")

        logging.debug("All tasks added, resuming scheduler")
        self.scheduler.resume()

    def update(self):
        active_schedule = self.fetch_active_schedule()

        if active_schedule is None:
            # pause scheduler since no schedules are active
            self.scheduler.pause()
            self.reset()
        else:
            self.update_jobs(active_schedule)

    def reset(self):
        self.scheduler.remove_all_jobs()
        self.board.disable()

    def start(self):
        if self.scheduler.running:
            logging.warn("Attempted to start the scheduler while it is already running")
            return

        self.scheduler.start()
        self.update()

    def stop(self):
        if not self.scheduler.running:
            logging.warn("Attempted to stop the scheduler while it is already stopped")
            return

        self.scheduler.shutdown(wait=False)
        self.board.disable()