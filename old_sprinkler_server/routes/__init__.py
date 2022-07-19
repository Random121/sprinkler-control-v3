from .api import api_blueprint, api_register
from .panel import panel_blueprint, panel_register
from .socketio import socketio_register


def create_routes(
    flask_app,
    flask_socketio,
    relay_board_controller,
    schedule_manager,
):
    api_register(flask_app, relay_board_controller, schedule_manager)
    panel_register(flask_app)
    socketio_register(flask_socketio, relay_board_controller)
