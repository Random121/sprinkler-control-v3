import atexit
from flask import Flask, render_template
from flask_restful import Api
from flask_cors import CORS
from flask_socketio import SocketIO, emit

import constants
from utils import get_lan_ip_address

flask_app = Flask(
    __name__,
    template_folder="public/template",
    static_folder="public/static",
)
flask_app.secret_key = constants.SECRET_KEY

flask_api = Api(flask_app, prefix=constants.SPRINKLER_API_URI)
flask_socketio = SocketIO(flask_app, cors_allowed_origins="*")
flask_cors = CORS(
    flask_app,
    resources=[
        f"{constants.SPRINKLER_API_URI}/*",
        f"{constants.SPRINKLER_SOCKET_URI}/*",
    ],
)


def main():
    print(f"Relay Control starting on http://{get_lan_ip_address()}:{constants.PORT}")
    flask_socketio.run(
        flask_app,
        host=constants.HOST,
        port=constants.PORT,
        debug=constants.DEBUG,
        use_reloader=constants.USE_RELOADER,
    )


if __name__ == "__main__":
    main()
