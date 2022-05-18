from flask_socketio import SocketIO, emit, disconnect

from models.Events import EventEmitter
from models.RelayControl import RelayBoardController


class RelaySocketio:
    def __init__(
        self,
        socketio: SocketIO,
        socketio_namespace: str,
        relay_board_controller: RelayBoardController,
    ) -> None:
        self.socketio = socketio
        self.namespace = socketio_namespace
        self.board_controller = relay_board_controller

        self.define_routes()

        EventEmitter.on("relay_update", self.send_relay_update)

    def define_routes(self):

        @self.socketio.on("connect", namespace=self.namespace)
        def on_connect():
            emit("relay_update", self.board_controller.get_info())

        @self.socketio.on("relay_action", namespace=self.namespace)
        def on_relay_action(action_request: dict):
            pass

        @self.socketio.on("schedule_action", namespace=self.namespace)
        def on_schedule_action(action_request: dict):
            pass

    def send_relay_update(self):
        self.socketio.emit(
            "relay_update",
            self.board_controller.get_info(),
            namespace=self.namespace,
        )
