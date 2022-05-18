DEBUG = True
USE_RELOADER = False

HOST = "0.0.0.0"
PORT = 42488

SECRET_KEY = "6acd1bb4899753e108b315d5f8a147edd4f958d17523278a0ff18d180ef65922"

SPRINKLER_API_URI = "/v1/api/sprinklers"
SPRINKLER_SOCKET_URI = "/v1/socketio/sprinklers"

RELAY_PINOUT = {
    "GPIO_6": 6,
    "GPIO_13": 13,
    "GPIO_19": 19,
    "GPIO_26": 26,
}
