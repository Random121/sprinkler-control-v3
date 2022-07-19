import test_constants as constants
from models.RelayControl.controller_new import RelayBoardController
from resources.socketio import RelayUpdateSocketIO

from flask_socketio import SocketIO


def socketio_register(
    flask_socketio: SocketIO,
    relay_board_controller: RelayBoardController,
):
    socketio_resource = RelayUpdateSocketIO(
        flask_socketio,
        constants.SOCKETIO_UPDATE_PATH,
        relay_board_controller,
    )
