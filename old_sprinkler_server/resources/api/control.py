from flask_restful import Resource, reqparse

from .utils import call_controller
from models.RelayControl.controller_new import RelayBoardController

post_parser = reqparse.RequestParser(
    trim=True,
    bundle_errors=True,
)
post_parser.add_argument(
    "action",
    type=str,
    help="Action is required",
    required=True,
)
post_parser.add_argument(
    "arguments",
    type=dict,
    help="Arguments are required",
    required=True,
)


class RelayAPI(Resource):
    def __init__(self, relay_board_controller: RelayBoardController) -> None:
        self.controller = relay_board_controller

    def get(self, relay_id: str):
        return call_controller(self.controller.get_info, relay_id)

    def post(self, relay_id: str):
        action: dict = post_parser.parse_args()

        # TODO: find a better way to pass the relay id
        action["arguments"]["id"] = relay_id

        call_controller(self.controller.dispatch, action)


class RelayListAPI(Resource):
    def __init__(self, relay_board_controller: RelayBoardController) -> None:
        self.controller = relay_board_controller

    def get(self):
        return call_controller(self.controller.get_info, None)

    def post(self):
        action: dict = post_parser.parse_args()

        # TODO: find a better way to pass the relay id
        action["arguments"]["id"] = None

        call_controller(self.controller.dispatch, action)
