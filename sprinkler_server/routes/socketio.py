from typing import Union
from flask_socketio import Namespace, SocketIO

import sprinkler_config as config
from sprinkler_server import relay_board_controller

# shorthand variables
namespace = config.SOCKETIO_UPDATE_PATH
controller = relay_board_controller


class UpdateNamespace(Namespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        controller.board.emitter.on("update", self._send_update)

    def _send_update(self, ids: Union[list, None] = None):
        infos = controller.get_info(ids)
        self.emit("update", infos)

    def on_connect(self):
        self._send_update()

    def on_request_update(self, ids: Union[list, None] = None):
        self._send_update(ids)


def socketio_register(socketio: SocketIO):
    socketio.on_namespace(UpdateNamespace(namespace))
