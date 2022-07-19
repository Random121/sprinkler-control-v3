from types import MethodType

from models.Normalizer import ActionNormalizer
from models.Relay.board import RelayBoard


class RelayBoardController:
    def __init__(
        self,
        relay_board: RelayBoard,
        action_normalizer: ActionNormalizer,
        relay_info_mapping: dict[str, dict],
    ) -> None:
        self.board = relay_board
        self.normalizer = action_normalizer
        self.info_mapping = relay_info_mapping

    def dispatch(self, action: dict):
        action = self.normalizer.normalize(action)

        method_name: str = action.get("method")
        method: MethodType = getattr(self.board, method_name, None)

        if not isinstance(method, MethodType):
            raise TypeError(f"Method {method_name} is {type(method)}")

        method(*(action.get("arguments")))

    # additional information added to state (name, pin, etc)
    def get_info(self, ids: (str | list | None) = None):
        states = self.board.get_state(ids)

        for state in states:
            id = state.get("id")
            info = self.info_mapping.get(id)
            state.update(info)

        return states
