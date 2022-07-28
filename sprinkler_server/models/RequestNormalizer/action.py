from sprinkler_server.exceptions import MissingArgument
from sprinkler_server.utils import build_jsonschema_validator


class ActionNormalizer:
    def __init__(self, templates: list[dict], action_schema: dict) -> None:
        self.method_lookup = {}
        self.arguments_lookup = {}
        self.validate_action = build_jsonschema_validator(action_schema)

        self._build_lookup_tables(templates)

    def _build_lookup_tables(self, templates: list[dict]):
        template: dict  # for type annotation
        for template in templates:
            action_names: list[str] = template.get("action")
            method: str = template.get("method")
            arguments: list[dict] = template.get("arguments", [])

            if action_names is None:
                raise KeyError("Action names are missing from template")

            if method is None:
                raise KeyError("Method is missing from template")

            # build lookup table to map an action to its method
            for name in action_names:
                self.method_lookup[name] = method

            # allow arguments for a method name to be looked up
            self.arguments_lookup[method] = arguments

    def normalize(self, action: dict) -> dict:
        self.validate_action(action)

        action_name: str = action.get("action")
        method_name: str = self.lookup_method(action_name)
        arguments: list = self.parse_arguments(method_name, action.get("arguments"))

        return {
            "action": action_name,
            "method": method_name,
            "arguments": arguments,
        }

    def lookup_method(self, action: str):
        if action is None:
            raise TypeError("Missing action")

        if not isinstance(action, str):
            raise TypeError(f"Action must be a string not {type(action)}")

        method: str = self.method_lookup.get(action)

        if method is None:
            raise TypeError(f"No method for action {action}")

        return method

    def parse_arguments(self, method: str, arguments: dict):
        if arguments is None:
            raise TypeError("Missing arguments")

        if not isinstance(arguments, dict):
            raise TypeError("Arguments must be a dictionary")

        template_arguments: list[dict] = self.arguments_lookup.get(method)
        parsed_arguments = []

        for argument in template_arguments:
            name: str = argument.get("name")
            required: bool = argument.get("required", False)

            value = arguments.get(name)

            if required and value is None:
                raise MissingArgument(f"Missing {name} argument")

            parsed_arguments.append(value)

        return parsed_arguments
