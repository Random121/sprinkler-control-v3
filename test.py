from time import sleep
from models.Relay import RelayBoard
from gpiozero.pins.mock import MockFactory
from pprint import pprint

RELAY_PINOUT = {
    "GPIO_6": 6,
    "GPIO_13": 13,
    "GPIO_19": 19,
    "GPIO_26": 26,
}

board = RelayBoard(RELAY_PINOUT, pin_factory=MockFactory())

board.enable(["GPIO_26"], 19)

pprint(board.get_info())

board.enable(["GPIO_19"], 19)

pprint(board.get_info())