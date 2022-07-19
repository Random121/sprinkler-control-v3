import re
import logging
import traceback
from typing import Callable
from jsonschema import ValidationError
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
    except SprinklerExeception:
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
    help="Schedule to add is required",
    required=True,
)

relay_scheduler_patch_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_scheduler_patch_parser.add_argument(
    "schedule_id",
    type=str,
    help="Identifier of schedult to set active is required",
    required=True,
)

relay_scheduler_delete_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_scheduler_delete_parser.add_argument(
    "schedule_id",
    type=str,
    help="Identifier of schedult to delete is required",
    required=True,
)

relay_scheduler_put_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
relay_scheduler_delete_parser.add_argument(
    "schedule_id",
    type=str,
    help="Identifier of schedult to delete is required",
    required=True,
)
relay_scheduler_delete_parser.add_argument(
    "schedule",
    type=str,
    help="Replacement schedule is required",
    required=True,
)

# errors can be found in https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/_validators.py
missing_property_re = re.compile("^(?P<value>'.+?') is a required property$")
additional_property_re = re.compile(
    "^Additional properties are not allowed \((?P<value>.+?) (was|were) unexpected\)$"
)

extra_value_parsers = {
    "required": [missing_property_re, "missing_property"],
    "additionalProperties": [additional_property_re, "additional_properties"],
}


def parse_extra_values(validator, error_message: str):
    extra_values = {}

    parser = extra_value_parsers.get(validator)
    if parser is None:
        return extra_values

    name: str = parser[1]
    value: str = parser[0].match(error_message).group("value")

    logging.info(value)
    logging.info(error_message)

    return {name: value}


def get_schema_error_message(error: ValidationError):
    schema: dict = error.schema
    validator = error.validator
    default_error_message = error.message

    # use optional chaining to get custom error message
    # else use default provided by jsonschema
    error_message: str = schema.get("errorMessage", {}).get(
        validator, default_error_message
    )

    return error_message.format(
        default_message=default_error_message,
        instance=error.instance,
        validator=validator,
        validator_value=error.validator_value,
        **parse_extra_values(validator, default_error_message),
    )


# api for controlling scheduler
class SchedulerControlApi(Resource):
    def __init__(self, scheduler_manager: SchedulerManager) -> None:
        self.manager = scheduler_manager

    # get all schedules
    def get(self):
        return self.manager.get_schedules()

    # add new schedule
    def post(self):
        schedule_request: dict = relay_scheduler_post_parser.parse_args()
        schedule: dict = schedule_request["schedule"]

        # TODO: implement custom error messages with json schema
        try:
            self.manager.add_schedule(schedule)
        except ValidationError as err:
            abort(422, message=get_schema_error_message(err))

    # delete schedule
    def delete(self):
        delete_request: dict = relay_scheduler_delete_parser.parse_args()
        schedule_id: str = delete_request["schedule_id"]

        if not self.manager.is_schedule(schedule_id):
            abort(422, message=f"No schedule found with identifier {schedule_id}")

        self.manager.remove_schedule(schedule_id)

    # set active schedule
    def patch(self):
        patch_request: dict = relay_scheduler_patch_parser.parse_args()
        schedule_id: str = patch_request["schedule_id"]

        if not self.manager.is_schedule(schedule_id):
            abort(422, message=f"No schedule found with identifier {schedule_id}")

        self.manager.set_active(schedule_id)

    # replace a schedule
    def put(self):
        put_request: dict = relay_scheduler_put_parser.parse_args()
        schedule_id: str = put_request["schedule_id"]
        schedule: dict = put_request["schedule"]

        if not self.manager.is_schedule(schedule_id):
            abort(422, message=f"No schedule found with identifier {schedule_id}")

        self.manager.update_schedule(schedule_id, schedule)
