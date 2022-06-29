import atexit
import logging
from threading import Timer
from flask import Flask, render_template
from flask_restful import Api
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from gpiozero.pins.mock import MockFactory

import constants
from models.Scheduler import Scheduler
from models.Parser import ActionRequestParser
from models.Relay import RelayBoard
from models.RelayControl import RelayBoardController
from resources.api import RelayControlApi
from resources.socketio import RelaySocketio
from utils import get_lan_ip_address

try:
    # patch eventlet so threading will work
    import eventlet
    eventlet.monkey_patch()
except ImportError:
    logging.error("Failed to import and monkey patch eventlet")
    exit()

flask_app = Flask(
    __name__,
    template_folder="public/template",
    static_folder="public/static",
)
flask_app.secret_key = constants.SECRET_KEY

flask_api = Api(flask_app, prefix=constants.SPRINKLER_API_URI)
flask_socketio = SocketIO(flask_app, cors_allowed_origins="*")
flask_cors = CORS(
    flask_app,
    resources=[
        f"{constants.SPRINKLER_API_URI}/*",
        f"{constants.SPRINKLER_SOCKET_URI}/*",
    ],
)

relay_board = RelayBoard(pinout=constants.RELAY_PINOUT, pin_factory=MockFactory())
relay_action_parser = ActionRequestParser(templates=constants.RELAY_ACTION_TEMPLATES_V1)
relay_board_controller = RelayBoardController(relay_board=relay_board, relay_action_parser=relay_action_parser)

relay_scheduler = Scheduler(relay_board=relay_board)

socketio_resource = RelaySocketio(
    flask_socketio,
    constants.SPRINKLER_SOCKET_URI,
    relay_board_controller,
)

flask_api.add_resource(
    RelayControlApi,
    "/",
    "/<string:relay_id>",
    resource_class_args=tuple([relay_board_controller]),
)


@flask_app.route("/")
def control_panel_page():
    return render_template(
        "index.html",
        api_address=constants.SPRINKLER_API_URI,
        socketio_address=constants.SPRINKLER_SOCKET_URI,
    )


@atexit.register
def clean_up():
    """
    reset all relays before python shutdown
    """
    relay_board.disable()
    logging.info("[SUCCESSFULLY CLEAN UP]")

def main():
    print(f"Relay Control starting on http://{get_lan_ip_address()}:{constants.PORT}")
    flask_socketio.run(
        flask_app,
        host=constants.HOST,
        port=constants.PORT,
        debug=constants.DEBUG,
        use_reloader=constants.USE_RELOADER,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(asctime)s] - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    relay_scheduler.start()
    main()
