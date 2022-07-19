from datetime import datetime
from socket import socket, AF_INET, SOCK_DGRAM
from jsonschema import exceptions, Validator
from jsonschema.validators import validator_for


def get_lan_ip_address():
    socket_server = socket(AF_INET, SOCK_DGRAM)
    try:
        # ip does not have to be reachable
        socket_server.connect(("10.255.255.255", 1))
        local_ip = socket_server.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        socket_server.close()
    return local_ip


# slightly more optimized jsonschema validator which doesn't recreate
# the validator class every function call
def build_jsonschema_validator(schema: dict, *args, **kwargs):
    _validator_class: Validator = validator_for(schema=schema)
    _validator_class.check_schema(schema=schema)
    _validator: Validator = _validator_class(schema, *args, **kwargs)

    def validator(instance):
        error = exceptions.best_match(_validator.iter_errors(instance))
        if error is not None:
            raise error

    return validator


def parse_relay_config(relay_config: list[dict]):
    pin_mapping = {}
    info_mapping = {}

    for item in relay_config:
        id = item.get("id")
        pin = item.get("pin")

        pin_mapping[id] = pin
        info_mapping[id] = item

    return pin_mapping, info_mapping
