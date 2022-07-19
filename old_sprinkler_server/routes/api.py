import test_constants as constants
from models.RelayControl.controller_new import RelayBoardController
from models.Scheduler.manager import ScheduleManager

from resources.api import (
    RelayAPI,
    RelayListAPI,
    ScheduleAPI,
    ScheduleListAPI,
    ActiveScheduleAPI,
)

from flask import Flask, Blueprint
from flask_restful import Api

api_blueprint = Blueprint(
    "api",
    __name__,
    url_prefix=constants.API_BASE_PATH,
)

api = Api(api_blueprint)


def api_register(
    flask_app: Flask,
    relay_board_controller: RelayBoardController,
    schedule_manager: ScheduleManager,
):
    flask_app.register_blueprint(api_blueprint)

    api.add_resource(
        RelayAPI,
        f"{constants.API_CONTROL_ENDPOINT}/<string:relay_id>",
        resource_class_args=tuple([relay_board_controller]),
    )

    api.add_resource(
        RelayListAPI,
        f"{constants.API_CONTROL_ENDPOINT}/",
        resource_class_args=tuple([relay_board_controller]),
    )

    api.add_resource(
        ScheduleAPI,
        f"{constants.API_SCHEDULE_ENDPOINT}/<string:schedule_id>",
        resource_class_args=tuple([schedule_manager]),
    )

    api.add_resource(
        ScheduleListAPI,
        f"{constants.API_SCHEDULE_ENDPOINT}/",
        resource_class_args=tuple([schedule_manager]),
    )

    api.add_resource(
        ActiveScheduleAPI,
        f"{constants.API_SCHEDULE_ENDPOINT}/active/",
        f"{constants.API_SCHEDULE_ENDPOINT}/active/<string:schedule_id>",
        resource_class_args=tuple([schedule_manager]),
    )
