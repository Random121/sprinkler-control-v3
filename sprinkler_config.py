# RESTful API configurations
API_VERSION = "v1"
API_BASE_PATH = f"/sprinkler/{API_VERSION}/api"

API_CONTROL_ENDPOINT = "/relays"
API_SCHEDULE_ENDPOINT = "/schedules"

API_CONTROL_PATH = f"{API_BASE_PATH}{API_CONTROL_ENDPOINT}"
API_SCHEDULE_PATH = f"{API_BASE_PATH}{API_SCHEDULE_ENDPOINT}"

# SocketIO configurations
SOCKETIO_VERSION = "v1"
SOCKETIO_BASE_PATH = f"/sprinkler/{SOCKETIO_VERSION}/socketio"

SOCKETIO_UPDATE_ENDPOINT = "/update"

SOCKETIO_UPDATE_PATH = f"{SOCKETIO_BASE_PATH}{SOCKETIO_UPDATE_ENDPOINT}"

# MongoDB configurations
MONGODB_URL = (
    "mongodb+srv://user:user@cluster0.di3hb.mongodb.net/?retryWrites=true&w=majority"
)

# Relay configurations
RELAY_CONFIG = [
    {
        "id": "GPIO_6",
        "name": "GPIO 6",
        "pin": 6,
    },
    {
        "id": "GPIO_13",
        "name": "GPIO 13",
        "pin": 13,
    },
    {
        "id": "GPIO_19",
        "name": "GPIO 19",
        "pin": 19,
    },
    {
        "id": "GPIO_26",
        "name": "GPIO 26",
        "pin": 26,
    },
]

ACTION_TEMPLATE_V2 = [
    {
        "action": ["enable"],
        "method": "enable",
        "arguments": [
            {
                "name": "id",
                "required": True,
            },
            {
                "name": "duration",
                "required": True,
            },
        ],
    },
    {
        "action": ["disable"],
        "method": "disable",
        "arguments": [
            {
                "name": "id",
                "required": True,
            }
        ],
    },
]
