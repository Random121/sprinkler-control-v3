from models.Relay import RelayBoard

RELAY_PINOUT = {
    "GPIO_6": 6,
    "GPIO_13": 13,
    "GPIO_19": 19,
    "GPIO_26": 26,
}

board = RelayBoard(RELAY_PINOUT)

board.enable(["GPIO_6"], 10)