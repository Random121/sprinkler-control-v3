from types import MethodType
from models.Relay import RelayBoard
from exceptions import *


class RelayBoardController:
    def __init__(self, relay_board: RelayBoard) -> None:
        self.board = relay_board

    # NOTE: action request received by this function must be parsed
    def dispatch_action(self, action_request: dict):

        if "method" not in action_request:
            raise Exception(f"Action request is not parsed")

        method_name: str = action_request.get("method")
        method: MethodType = getattr(self.board, method_name, None)

        if not isinstance(method, MethodType):
            raise InvalidAction(f"Method {method_name} is {type(method)}")

        method(*(action_request.get("arguments")))

    # easier way for internal code to request the relay board's info
    def get_info(self, id: list = None):
        return self.board.get_info(id)
