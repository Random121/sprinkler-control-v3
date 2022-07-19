import logging
import dateutil.parser
from pymongo.collection import Collection
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from sprinkler_server.models.Relay import RelayBoard


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

        logging.info(
            f"Updating {len(schedule_tasks)} tasks for schedule {schedule_id} ({schedule_name})"
        )

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
