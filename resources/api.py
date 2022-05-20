import traceback
from typing import Callable
from flask_restful import abort, Resource, reqparse

import constants
from exceptions import *
from models.Events import EventEmitter
from models.RelayControl import RelayBoardController

relay_post_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_post_parser.add_argument(
    "action_name",
    type=str,
    help="Action is required",
    required=True,
)
relay_post_parser.add_argument(
    "arguments",
    type=dict,
    help="Arguments list is required (even if empty)",
    required=True
)

# api for controlling relays
class RelayControlApi(Resource):
    def __init__(self, relay_board_controller: RelayBoardController) -> None:
        super().__init__()
        self.board_controller = relay_board_controller

    # handles the exceptions raised when a board controller
    # function is called
    def safe_call(self, function: Callable, *args, **kwargs):
        try:
            function(*args, **kwargs)
        except InvalidAction:
            abort(400, message="Specified action is invalid")
        except InvalidRelay:
            abort(400, message="Specified relay is invalid")
        except InvalidActionRequest:
            abort(400, message="Action request is in an invalid format")
        except MissingRequiredArgument:
            abort(400, message="Action request is missing required argument(s)")
        except InvalidRelayDuration:
            abort(400, message="Duration must be greater than 0")
        except SprinklerControlBaseException:
            print(f"[UNHANDLED EXCEPTION] {traceback.format_exc()}", flush=True)

    def get(self, relay_id: str):
        self.safe_call(self.board_controller.get_info, relay_id)

    def post(self, relay_id: str):
        action_request: dict = relay_post_parser.parse_args()

        # allow flexible insertion of relay id
        if "relay_id" not in action_request["arguments"]:
            action_request["arguments"]["relay_id"] = relay_id

        self.safe_call(self.board_controller.dispatch_action, action_request)

        EventEmitter.emit("relay_update")

# api for controlling scheduler
class SchedulerControlApi(Resource):
    def __init__(self, scheduler_manager) -> None:
        super().__init__()