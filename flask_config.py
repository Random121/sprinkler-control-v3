import logging


class DebugConfig(object):
    DEBUG = True
    TESTING = True
    USE_RELOADER = True

    HOST = "127.0.0.1"
    PORT = 42488

    SECRET_KEY = "SPRINKLER_DEBUG"

    LOGGING_CONFIG = {
        "level": logging.DEBUG,
        "format": "[%(asctime)s] - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }


class ProductionConfig(object):
    DEBUG = False
    TESTING = False
    USE_RELOADER = False

    HOST = "0.0.0.0"
    PORT = 42488

    SECRET_KEY = "90502c52eeb185f4e709069413f260393ba741b5637f6f026da97df7fa489e40d644ebc8382459e0823994a39d08ca006d4aa7a58b9e0453b4129af7904fddbb"

    LOGGING_CONFIG = {
        "level": logging.INFO,
        "format": "[%(asctime)s] - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }
