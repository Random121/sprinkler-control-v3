# Sprinkler SocketIO
> Base URL:<br>
> `/sprinkler/v1/socketio`

<br>

## Relay Update Endpoint

> Update Structure:<br>
```python
[
    {
        "id": "MY_RELAY_1",
        "name": "My Backyard",
        "info": {
            "is_active": True | False,
            # time values are floats if the relay is active
            "duration": 60,
            "time_elapsed": 20,
            "time_remaining": 40
        }
    },
    {
        "id": "MY_RELAY_2",
        "name": "My Front Lawn",
        "info": {
            "is_active": True | False,
            # time values are None or null (in json) if the relay is not active
            "duration": None,
            "time_elapsed": None,
            "time_remaining": None
        }
    }
]
```

<br>

> `[SOCKETIO]` /update<br>
> The `Update Structure` is sent to the client in the `update` channel