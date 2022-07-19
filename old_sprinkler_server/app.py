import atexit
import logging
import eventlet
from flask import Flask, render_template
from flask_restful import Api
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from gpiozero.pins.pigpio import PiGPIOFactory

import constants
from models.Scheduler import Scheduler, SchedulerManager
from models.Parser import ActionRequestParser
from models.Relay import RelayBoard
from models.RelayControl import RelayBoardController
from resources.api import RelayControlApi, SchedulerControlApi
from resources.socketio import RelaySocketio
from utils import get_lan_ip_address

# patch eventlet so threading will work
eventlet.monkey_patch()

# patching pymongo because its trash
from pymongo import MongoClient

pymongo = eventlet.import_patched("pymongo")

flask_app = Flask(
    __name__,
    template_folder="public/template",
    static_folder="public/static",
)
flask_app.secret_key = constants.SECRET_KEY

flask_api = Api(flask_app, prefix=constants.SPRINKLER_BASE_API_URI)
flask_socketio = SocketIO(flask_app, cors_allowed_origins="*")
flask_cors = CORS(
    flask_app,
    resources=[
        f"{constants.SPRINKLER_BASE_API_URI}/*",
        f"{constants.SPRINKLER_BASE_SOCKETIO_URI}/*",
    ],
)

mongo_client: MongoClient = pymongo.MongoClient(
    "mongodb+srv://user:user@cluster0.di3hb.mongodb.net/?retryWrites=true&w=majority"
)
sprinkler_control_db = mongo_client["sprinkler_control"]
schedules_collection = sprinkler_control_db["schedules"]

relay_board = RelayBoard(pinout=constants.RELAY_PINOUT, pin_factory=PiGPIOFactory())
relay_action_parser = ActionRequestParser(templates=constants.RELAY_ACTION_TEMPLATES_V1)
relay_board_controller = RelayBoardController(
    relay_board=relay_board,
    relay_action_parser=relay_action_parser,
)

relay_scheduler = Scheduler(
    relay_board=relay_board,
    schedules_collection=schedules_collection,
)
relay_scheduler_manager = SchedulerManager(
    scheduler=relay_scheduler,
    schedules_collection=schedules_collection,
)

socketio_resource = RelaySocketio(
    flask_socketio,
    constants.SPRINKLER_CONTROL_SOCKET_URI,
    relay_board_controller,
)

flask_api.add_resource(
    RelayControlApi,
    f"{constants.SPRINKLER_CONTROL_PATH}/",
    f"{constants.SPRINKLER_CONTROL_PATH}/<string:relay_id>",
    resource_class_args=tuple([relay_board_controller]),
)

flask_api.add_resource(
    SchedulerControlApi,
    f"{constants.SPRINKLER_SCHEDULER_PATH}/",
    resource_class_args=tuple([relay_scheduler_manager]),
)


@flask_app.route("/")
def control_panel_page():
    return render_template(
        "index.html",
        api_address=constants.SPRINKLER_CONTROL_API_URI,
        socketio_address=constants.SPRINKLER_CONTROL_SOCKET_URI,
    )


@atexit.register
def clean_up():
    """
    reset all relays before python shutdown
    """
    relay_board.disable()
    relay_scheduler_manager.stop()
    mongo_client.close()
    logging.info("Sprinkler control has cleaned up")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info(
        f"Relay Control starting on http://{get_lan_ip_address()}:{constants.PORT}"
    )
    relay_scheduler_manager.start()
    flask_socketio.run(
        flask_app,
        host=constants.HOST,
        port=constants.PORT,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
