from types import MethodType
from models.Parser import ActionRequestParser
from models.Relay import RelayBoard
from exceptions import *


class RelayBoardController:
    def __init__(
        self,
        relay_board: RelayBoard,
        relay_action_parser: ActionRequestParser,
    ) -> None:
        self.board = relay_board
        self.parser = relay_action_parser

    def dispatch_action(self, action_request: dict):
        action_request = self.parser.parse(action_request)

        method_name: str = action_request.get("method_name")
        method: MethodType = getattr(self.board, method_name, None)

        if not isinstance(method, MethodType):
            raise InvalidAction(f"Method {method_name} is {type(method)}")

        method(*(action_request.get("arguments")))

    # easier way for internal code to request the relay board's info
    def get_info(self, id: list = None):
        return self.board.get_info(id)
