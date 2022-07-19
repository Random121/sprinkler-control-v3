import traceback
import logging
import re
from re import Pattern
from types import MethodType
from jsonschema import ValidationError
from flask_restful import abort

from exceptions import MissingArgument, SprinklerException


# errors can be found at https://github.com/python-jsonschema/jsonschema/blob/main/jsonschema/_validators.py
# use regex to the error message and name the match group as "value"
missing_property_re = re.compile("^(?P<value>'.+?') is a required property$")
additional_property_re = re.compile(
    "^Additional properties are not allowed \((?P<value>.+?) (was|were) unexpected\)$"
)

extra_value_parser_config: dict[str, dict[str, (str | Pattern)]] = {
    # validator name
    "required": {
        # regexp for the value
        "re": missing_property_re,
        # substitution variable name
        "substitute": "missing_property",
    },
    "additionalProperties": {
        "re": additional_property_re,
        "substitute": "additional_properties",
    },
}


def parse_extra_values(validator, error_message: str):
    parser = extra_value_parser_config.get(validator)

    if parser is None:
        return {}

    substitute: str = parser.get("substitute")
    value: str = parser.get("re").match(error_message).group("value")

    return {substitute: value}


def get_schema_error_message(error: ValidationError):
    schema: dict = error.schema
    validator = error.validator
    default_error_message = error.message

    # use optional chaining to get custom error message
    # else use default provided by jsonschema
    error_message: str = schema.get("errorMessage", {}).get(
        validator,
        default_error_message,
    )

    return error_message.format(
        default_message=default_error_message,
        instance=error.instance,
        validator=validator,
        validator_value=error.validator_value,
        **parse_extra_values(validator, default_error_message),
    )


# handles all errors from the controller
def call_controller(method: MethodType, *args, **kwargs):
    try:
        return method(*args, **kwargs)
    except (TypeError, KeyError, ValueError, MissingArgument) as error:
        abort(422, message=str(error))
    except ValidationError as error:
        abort(400, message=get_schema_error_message())
    except SprinklerException:
        logging.error(f"[UNHANDLED EXCEPTION] {traceback.format_exc()}")
