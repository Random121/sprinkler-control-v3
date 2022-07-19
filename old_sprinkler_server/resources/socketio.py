import logging
import traceback
from flask_socketio import SocketIO, emit, disconnect

from exceptions import *
from models.Parser import ActionRequestParser
from models.RelayControl import RelayBoardController


class RelaySocketio:
    def __init__(
        self,
        socketio: SocketIO,
        socketio_namespace: str,
        relay_board_controller: RelayBoardController,
        name_mapping: dict[str, str],
    ) -> None:
        self.socketio = socketio
        self.namespace = socketio_namespace
        self.name_mapping = name_mapping

        self.board_controller = relay_board_controller
        self.board_controller.board.emitter.on("update", self.send_relay_update)

        self.define_routes()

    def define_routes(self):
        @self.socketio.on("connect", namespace=self.namespace)
        def on_connect():
            self.send_relay_update()

        @self.socketio.on("relay_action", namespace=self.namespace)
        def on_relay_action(action_request: dict):
            try:
                self.board_controller.dispatch_action(action_request)
            except SprinklerExeception:
                logging.error(f"[SOCKETIO ERR] {traceback.format_exc()}")

        @self.socketio.on("schedule_action", namespace=self.namespace)
        def on_schedule_action(action_request: dict):
            pass

    def send_relay_update(self, ids: list = None):
        infos = self.board_controller.get_info(ids)

        for info in infos:
            info["name"] = self.name_mapping[info["id"]]

        self.socketio.emit("update", infos, namespace=self.namespace)
