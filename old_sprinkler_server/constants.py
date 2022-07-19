DEBUG = True
USE_RELOADER = False

HOST = "0.0.0.0"
PORT = 42488

SECRET_KEY = "6acd1bb4899753e108b315d5f8a147edd4f958d17523278a0ff18d180ef65922"

SPRINKLER_BASE_API_URI = "/v1/api/sprinklers"
SPRINKLER_BASE_SOCKETIO_URI = "/v1/socketio/sprinklers"

SPRINKLER_CONTROL_PATH = "/control"
SPRINKLER_SCHEDULER_PATH = "/schedule"

SPRINKLER_CONTROL_API_URI = f"{SPRINKLER_BASE_API_URI}{SPRINKLER_CONTROL_PATH}"
SPRINKLER_CONTROL_SOCKET_URI = f"{SPRINKLER_BASE_SOCKETIO_URI}{SPRINKLER_CONTROL_PATH}"

RELAY_PINOUT = {
    "GPIO_6": 6,
    "GPIO_13": 13,
    "GPIO_19": 19,
    "GPIO_26": 26,
}

RELAY_ACTION_TEMPLATES_V1 = [
    {
        "action_name": ["enable"],
        "method_name": "enable",
        "required_arguments": ["relay_id", "duration"],
    },
    {
        "action_name": ["disable"],
        "method_name": "disable",
        "required_arguments": ["relay_id"],
    },
    # {
    #     "action_name": ["cancel_timer"],
    #     "method_name": "cancel_timer",
    #     "required_arguments": ["relay_id"],
    # },
]
