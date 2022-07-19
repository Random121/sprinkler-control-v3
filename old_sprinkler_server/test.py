import atexit
import logging
import eventlet
from pymongo import MongoClient
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from gpiozero.pins.mock import MockFactory

import test_constants as constants
from utils import get_lan_ip_address, parse_config

from models.Scheduler import Scheduler, ScheduleManager
from models.Normalizer import ActionNormalizer
from models.Relay.board_new import RelayBoard
from models.RelayControl.controller_new import RelayBoardController

from routes import create_routes

# patch eventlet so threading will work
eventlet.monkey_patch()

# patching pymongo because its trash
pymongo = eventlet.import_patched("pymongo")

flask_app = Flask(
    __name__,
    template_folder="public/template",
    static_folder="public/static",
)
flask_socketio = SocketIO(flask_app, cors_allowed_origins="*")
flask_cors = CORS(
    flask_app,
    resources=[f"{constants.API_BASE_PATH}/*", f"{constants.SOCKETIO_BASE_PATH}/*"],
)

mongo_client: MongoClient = pymongo.MongoClient(constants.MONGODB_URL)
sprinkler_control_db = mongo_client["test_sprinkler"]
schedules_collection = sprinkler_control_db["test_schedules"]

pin_mapping, info_mapping = parse_config(constants.RELAY_CONFIG)

action_normalizer = ActionNormalizer(constants.ACTION_TEMPLATE_V2)
relay_board = RelayBoard(pin_mapping, pin_factory=MockFactory())
relay_board_controller = RelayBoardController(
    relay_board,
    action_normalizer,
    info_mapping,
)


scheduler = Scheduler(
    relay_board=relay_board,
    schedules_collection=schedules_collection,
)
schedule_manager = ScheduleManager(
    scheduler=scheduler,
    schedules_collection=schedules_collection,
)


@atexit.register
def clean_up():
    """
    reset all relays before python shutdown
    """
    relay_board.disable()
    schedule_manager.stop()
    mongo_client.close()
    logging.info("Sprinkler control has cleaned up")


def main():
    logging.basicConfig(**constants.LOGGING_CONFIG)
    logging.info(f"Starting on http://{get_lan_ip_address()}:{constants.FLASK_PORT}")

    create_routes(flask_app, flask_socketio, relay_board_controller, schedule_manager)
    schedule_manager.start()
    flask_socketio.run(
        flask_app,
        host=constants.FLASK_HOST,
        port=constants.FLASK_PORT,
        debug=constants.FLASK_DEBUG,
        use_reloader=constants.FLASK_USE_RELOADER,
    )


if __name__ == "__main__":
    main()
