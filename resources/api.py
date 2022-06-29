import random
import logging
import sched
import traceback
from typing import Callable
from flask_restful import abort, Resource, reqparse

import constants
from exceptions import *
from models.Parser import ActionRequestParser
from models.RelayControl import RelayBoardController
from models.Scheduler import SchedulerManager

relay_control_post_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_control_post_parser.add_argument(
    "action_name",
    type=str,
    help="Action is required",
    required=True,
)
relay_control_post_parser.add_argument(
    "arguments",
    type=dict,
    help="Arguments list is required (even if empty)",
    required=True,
)


# handles the exceptions raised when a board controller
# function is called
def board_controller_call(function: Callable, *args, **kwargs):
    try:
        return function(*args, **kwargs)
    except InvalidAction:
        abort(422, message="Specified action is invalid")
    except InvalidRelay:
        print(traceback.format_exc())
        abort(422, message="Specified relay is invalid")
    except InvalidActionRequest:
        abort(422, message="Action request is in an invalid format")
    except MissingRequiredArgument:
        abort(422, message="Action request is missing required argument(s)")
    except InvalidRelayDuration:
        abort(422, message="Duration must be greater than 0")
    except SprinklerControlBaseException:
        logging.error(f"[UNHANDLED EXCEPTION] {traceback.format_exc()}")


# api for controlling relays
class RelayControlApi(Resource):
    def __init__(self, relay_board_controller: RelayBoardController) -> None:
        self.board_controller = relay_board_controller

    def get(self, relay_id: str = None):
        return board_controller_call(self.board_controller.get_info, relay_id)

    def post(self, relay_id: str = None):
        action_request: dict = relay_control_post_parser.parse_args()

        # more flexibility in where relay_id is specified
        if "relay_id" not in action_request["arguments"]:
            action_request["arguments"]["relay_id"] = relay_id

        board_controller_call(self.board_controller.dispatch_action, action_request)


relay_scheduler_post_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_scheduler_post_parser.add_argument(
    "schedule",
    type=dict,
    help="The new schedule is required",
    required=True,
)

relay_scheduler_patch_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_scheduler_patch_parser.add_argument(
    "state",
    type=bool,
    help="Active state of schedule (true=enable, false=disable) is required",
    required=True,
)
relay_scheduler_patch_parser.add_argument(
    "schedule_id",
    type=str,
    help="Schedule ID is required",
    required=True,
)

relay_scheduler_delete_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_scheduler_delete_parser.add_argument(
    "schedule_id",
    type=str,
    help="Schedule ID is required",
    required=True,
)

# api for controlling scheduler
class SchedulerControlApi(Resource):
    def __init__(self, scheduler_manager: SchedulerManager) -> None:
        self.manager = scheduler_manager

    # get all schedules
    def get(self):
        schedules: list = self.manager.get_all_schedules()
        for schedule in schedules:
            del schedule["_id"]
        return schedules

    # add new schedule
    def post(self):
        schedule_request: dict = relay_scheduler_post_parser.parse_args()
        schedule: dict = schedule_request["schedule"]

        # randomly generate a schedule name (which currently acts as an ID)
        if "name" not in schedule:
            schedule["name"] = f"Schedule #{str(random.random())[2:]}"

        if self.manager.is_schedule({ "name": schedule["name"] }):
            abort(422, message=f"Schedule with name {schedule['name']} already exists")

        if "days" not in schedule:
            abort(422, message="Schedule did not specify days to run")

        if "tasks" not in schedule:
            abort(422, message="Schedule did not specify any tasks")

        if "active" in schedule:
            abort(422, message="Schedule property active can only be specified by the server")

        schedule["active"] = False
        self.manager.add_schedule(schedule=schedule)

    # delete schedule
    def delete(self):
        delete_request: dict = relay_scheduler_delete_parser.parse_args()
        schedule_id: str = delete_request["schedule_id"]

        if schedule_id is None:
            abort(422, message="Missing ID of schedule to delete")

        self.manager.remove_schedule(schedule_id)


    # set active schedule
    def patch(self):
        patch_request: dict = relay_scheduler_patch_parser.parse_args()
        state: bool = patch_request["state"]
        schedule_id: str = patch_request["schedule_id"]

        if not isinstance(state, bool):
            abort(422, message=f"State must be bool but user sent {type(state)}")

        if not self.manager.is_schedule({ "name": schedule_id }):
            abort(422, message=f"Schedule with name {schedule_id} does not exist")

        self.manager.set_schedule_active_state(schedule_id, state)
