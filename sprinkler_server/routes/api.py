from flask import Blueprint
from flask_restful import Api

import sprinkler_config as config
from sprinkler_server import relay_board_controller, schedule_manager
from sprinkler_server.resources.api import (
    RelayAPI,
    RelayListAPI,
    ScheduleAPI,
    ScheduleListAPI,
    ActiveScheduleAPI,
)

controller_resource = tuple([relay_board_controller])
manager_resource = tuple([schedule_manager])

api_blueprint = Blueprint(
    "api",
    __name__,
    url_prefix=config.API_BASE_PATH,
)

api = Api(api_blueprint)

api.add_resource(
    RelayAPI,
    f"{config.API_CONTROL_ENDPOINT}/<string:relay_id>",
    resource_class_args=controller_resource,
)

api.add_resource(
    RelayListAPI,
    f"{config.API_CONTROL_ENDPOINT}/",
    resource_class_args=controller_resource,
)

api.add_resource(
    ScheduleAPI,
    f"{config.API_SCHEDULE_ENDPOINT}/<string:schedule_id>",
    resource_class_args=manager_resource,
)

api.add_resource(
    ScheduleListAPI,
    f"{config.API_SCHEDULE_ENDPOINT}/",
    resource_class_args=manager_resource,
)

api.add_resource(
    ActiveScheduleAPI,
    f"{config.API_SCHEDULE_ENDPOINT}/active/",
    f"{config.API_SCHEDULE_ENDPOINT}/active/<string:schedule_id>",
    resource_class_args=manager_resource,
)
