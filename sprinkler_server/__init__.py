import atexit
import json
import logging
import eventlet
from pymongo.mongo_client import MongoClient
# from gpiozero.pins.mock import MockFactory
from gpiozero.pins.pigpio import PiGPIOFactory

# patch eventlet so threading works
eventlet.monkey_patch()

# patch pymongo since it uses gevent by default
pymongo = eventlet.import_patched("pymongo")

from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO

import sprinkler_config as config
from .utils import parse_relay_config, get_lan_ip_address
from .models.Relay import RelayBoard
from .models.RelayControl import RelayBoardController
from .models.RequestNormalizer import ActionNormalizer
from .models.Scheduler import Scheduler, ScheduleManager


flask_socketio = SocketIO(cors_allowed_origins="*")
flask_cors = CORS()

mongo_client: MongoClient = pymongo.MongoClient(config.MONGODB_URL)
sprinkler_control_db = mongo_client["test_sprinkler"]
schedules_collection = sprinkler_control_db["test_schedules"]


with open("sprinkler_server/schemas/action.schema.json") as schema:
    ACTION_SCHEMA = json.load(schema)

with open("sprinkler_server/schemas/schedule.schema.json") as schema:
    SCHEDULE_SCHEMA = json.load(schema)

pin_mapping, info_mapping = parse_relay_config(config.RELAY_CONFIG)

action_normalizer = ActionNormalizer(config.ACTION_TEMPLATE_V2, ACTION_SCHEMA)
relay_board = RelayBoard(pin_mapping, pin_factory=PiGPIOFactory())
relay_board_controller = RelayBoardController(
    relay_board,
    action_normalizer,
    info_mapping,
)


scheduler = Scheduler(relay_board, schedules_collection)
schedule_manager = ScheduleManager(
    scheduler,
    schedules_collection,
    SCHEDULE_SCHEMA,
)


def create_app(flask_config: object):
    # create and configure flask
    flask_app = Flask(__name__)
    flask_app.config.from_object(flask_config)

    # initialize flask extensions
    flask_cors.init_app(flask_app)
    flask_socketio.init_app(flask_app)

    # register blueprints and other routes
    from .routes import api_blueprint, socketio_register, panel_blueprint

    flask_app.register_blueprint(api_blueprint)
    flask_app.register_blueprint(panel_blueprint)
    socketio_register(flask_socketio)

    # add additional routes
    @flask_app.route("/")
    def control_panel_redirect():
        return redirect(url_for("control_panel.default_page"))

    schedule_manager.start()

    server_ip = flask_config.HOST if flask_config.DEBUG else get_lan_ip_address()
    logging.info(f"Server on http://{server_ip}:{flask_config.PORT}")

    return flask_app, flask_socketio


@atexit.register
def cleanup():
    """
    reset all relays before python shutdown
    """
    relay_board.disable()
    schedule_manager.stop()
    mongo_client.close()
    logging.info("Cleaned up")
