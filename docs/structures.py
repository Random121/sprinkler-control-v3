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

SCHEDULE_FORMAT_V2 = {
    # unique ID for each schedule which is used internally
    "_id": "6b479aa3-c242-44f8-8751-956bf19b8fef",
    # non-unique user specified display name
    "name": "Schedule 1",
    # is this schedule supposed to be ran
    "active": True,
    # days of week on which the schedules runs
    # cron format: 0=sunday, 1=monday ... 6=saturday
    "days": [0, 3, 6],
    # list of relays to be run, when and how long to run them for
    "tasks": [
        {
            # 24 hour time with seconds being optional (00:00 - 23:59)
            # time which the relay will be enabled
            "start": "1:00",
            # how long the relay should stay enabled (seconds)
            # TODO: check for time overlap in the future
            "duration": 60,
            # id to relay to enable
            "id": "GPIO_6",
        },
        {
            "start": "2:30:45",
            "duration": 120,
            "id": "GPIO_13",
        },
    ],
}
