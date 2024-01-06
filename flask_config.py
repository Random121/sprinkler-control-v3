import logging
import os

from dotenv import load_dotenv

load_dotenv()

class DebugConfig(object):
    DEBUG = True
    USE_RELOADER = True

    HOST = "127.0.0.1"
    PORT = 42488

    SECRET_KEY = "SPRINKLER_DEBUG"

    LOGGING_CONFIG = {
        "level": logging.DEBUG,
        "format": "[%(asctime)s] - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "force": True,
    }


class ProductionConfig(object):
    DEBUG = False
    USE_RELOADER = False

    HOST = "0.0.0.0"
    PORT = 42488

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    LOGGING_CONFIG = {
        "level": logging.INFO,
        "format": "[%(asctime)s] - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "force": True,
    }
