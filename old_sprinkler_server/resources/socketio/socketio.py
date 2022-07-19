from flask_socketio import SocketIO

from models.RelayControl.controller_new import RelayBoardController


class RelayUpdateSocketIO:
    def __init__(
        self,
        socketio: SocketIO,
        namespace: str,
        relay_board_controller: RelayBoardController,
    ) -> None:
        self.socketio = socketio
        self.namespace = namespace
        self.controller = relay_board_controller

        self.controller.board.emitter.on("update", self.send_update)
        self.define_routes()

    def define_routes(self):
        @self.socketio.on("connect", namespace=self.namespace)
        def on_connect():
            self.send_update()

    def send_update(self, ids: (list | None) = None):
        states = self.controller.get_info(ids)
        self.socketio.emit("update", states, namespace=self.namespace)
