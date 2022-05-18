from exceptions import *


class ActionRequestParser:
    def __init__(self, templates: list) -> None:
        self.method_lookup = {}
        self.required_args_lookup = {}

        self.build_lookup_tables(templates)

    def parse(self, action_request: dict) -> dict:

        self.validate_request(action_request)

        action: str = action_request.get("action")

        method: str = self.lookup_method(action)
        arguments: list = self.parse_arguments(method, action_request.get("arguments"))

        return {
            "action": action,
            "method": method,
            "arguments": arguments,
        }

    def build_lookup_tables(self, templates: list):

        template: dict  # for type annotation
        for template in templates:
            method: str = template.get("method")

            # build method name lookup table
            for name in template.get("action"):
                self.method_lookup[name] = method

            # build required arg lookup table
            self.required_args_lookup[method] = template.get("required_arguments")

    def validate_request(self, action_request: dict):

        if not isinstance(action_request, dict):
            raise InvalidActionRequest(f"Wrong type ({type(action_request)})")

        if "method" in action_request:
            raise InvalidActionRequest(f"User sent method {action_request['method']}")

    def lookup_method(self, action: str):

        if action is None:
            raise InvalidAction("Missing action")

        if not isinstance(action, str):
            raise InvalidAction(f"Wrong type ({type(action)})")

        method: str = self.method_lookup.get(action)

        if method is None:
            raise InvalidAction(f"No method for action {action}")

        return method

    def parse_arguments(self, method: str, arguments: str):

        if arguments is None:
            raise InvalidActionRequest("Missing arguments list")

        if not isinstance(arguments, dict):
            raise InvalidActionRequest(f"Wrong type ({type(arguments)})")

        required_args: list = self.required_args_lookup.get(method)
        parsed_args = []

        if required_args:
            for name in required_args:
                if name not in arguments:
                    raise MissingRequiredArgument(name)

                parsed_args.append(arguments[name])

        return parsed_args