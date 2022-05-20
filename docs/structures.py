action_request = {
    "action_name": "action_name",
    "arguments": {
        "arg1": "val1",
        "arg2": "val2",
        "arg3": "val3",
    },
}

parsed_action_request = {
    "action_name": "action",
    "method_name": "method",
    "arguments": [
        "val1",
        "val2",
        "val3",
    ],
}

# NOTE: arguments are ordered and will be passed to the method in the order they are declared in the template
parsing_template = [
    {
        "action_name": ["action_name1", "action_name2", "action_name3"],
        "method_name": "method_name1",
        "required_arguments": ["arg1", "arg2", "arg3"],
    },
    {
        "action_name": ["action_name4", "action_name5", "action_name6"],
        "method_name": "method_name2",
        "required_arguments": ["arg1", "arg2", "arg3"],
    },
]
