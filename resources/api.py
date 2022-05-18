from flask_restful import abort, Resource, reqparse

import constants
from exceptions import *
from models.Events import EventEmitter
from models.RelayControl import RelayBoardController


# api controller for a single specified relay
class RelayControlApi(Resource):
    def __init__(self) -> None:
        super().__init__()
