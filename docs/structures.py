action_request = {
    "action": "action_name",
    "arguments": {
        "arg1": "val1",
        "arg2": "val2",
        "arg3": "val3",
    },
}

parsed_action_request = {
    "action": "action_name",
    "method": "method_name",
    "arguments": [
        "val1",
        "val2",
        "val3",
    ],
}

# NOTE: arguments are ordered and will be passed to the method in the order they are declared in the template
parsing_template = [
    {
        "action": ["action_name1", "action_name2", "action_name3"],
        "method": "method_name1",
        "required_arguments": ["arg1", "arg2", "arg3"],
    },
    {
        "action": ["action_name4", "action_name5", "action_name6"],
        "method": "method_name2",
        "required_arguments": ["arg1", "arg2", "arg3"],
    },
]
