import logging

from sprinkler_server import create_app
from flask_config import ProductionConfig

# NOTE: remember to change factory of relay board to a production factory
def main():
    config = ProductionConfig()
    logging.basicConfig(**config.LOGGING_CONFIG)
    flask_app, flask_socketio = create_app(config)
    flask_socketio.run(
        flask_app,
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=config.USE_RELOADER,
    )


if __name__ == "__main__":
    main()
