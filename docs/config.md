# Sprinkler Configuration

## Relay Configuration

```python
[
    {
        # unique identifier
        "id": "MY_RELAY_1",
        # name which is shown on panel
        "name": "My Backyard",
        # GPIO pin which it controls
        "pin": 1
    },
    {
        "id": "MY_RELAY_2",
        "name": "My Frontyard",
        "pin": 2
    }
]
```

## Action Template
This is a schema used to map an action to a corresponding method on the relay board. It also parses arguments and passes it to the method. Thus, the arguments specified in the action template must be ordered to be in the position they appear in the relay board method.

```python
[
    {
        # actions which map to the method
        "action": ["MY_ACTION"],
        # name of the method on the relay board
        "method": "MY_METHOD",
        # order dependant arguments
        "arguments": [
            {
                # name of the argument in the request arguments list
                "name": "MY_ARGUMENT_NAME",
                "required": True | False
            },
            {
                "name": "MY_OTHER_ARGUMENT_NAME",
                "required": True | False
            }
        ]
    }
]
```