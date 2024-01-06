# Sprinkler RESTful API
> Base URL:<br>
> `/sprinkler/v1/api`

## Relays Endpoints

> Action Structure:<br>
```python
{
    "action": "MY_ACTION",
    "arguments": {}
}
```

> `[GET]` /relays<br>
> Get status of all relays

> `[POST]` /relays<br>
> Perform an action on all relays

> `[GET]` /relays/{relay_id}<br>
> Get status of relay specified by `relay_id`

> `[POST]` /relays/{relay_id}<br>
> Perform an action on relay specified by `relay_id`<br>
> The `enable` action requires a `duration` argument (in seconds)

## Scheduler Endpoints

> Schedule Structure:
```python
{
    # UUID for each schedule which is used in the API
    # NOTE: the client should not specify this value
    "_id": "6b479aa3-c242-44f8-8751-956bf19b8fef",
    # non-unique user specified display name
    "name": "My Schedule",
    # is this schedule supposed to be ran
    "active": True | False,
    # days of week to run
    # 0=sunday, 1=monday ... 6=saturday
    "days": [0, 1, 2, 3, 4, 5, 6],
    "tasks": [
        {
            # 24-hour time with seconds being optional (00:00 - 23:59)
            # time which the relay will be enabled
            "start": "12:00",
            # how long the relay should stay enabled (seconds)
            "duration": 120,
            # ID to relay to enable
            "id": "MY_RELAY_1"
        },
        {
            "start": "1:00",
            "duration": 180,
            "id": "MY_RELAY_2"
        }
    ]
}
```

<br>

> `[GET]` /schedules<br>
> Get all schedules

<br>

> `[POST]` /schedules<br>
> Add a new schedule which follows the `Schedule Structure`

<br>

> `[GET]` /schedules/{schedule_id}<br>
> Get information about schedule specified by `schedule_id`

<br>

> `[DELETE]` /schedules/{schedule_id}<br>
> Deletes the schedule specified by `schedule_id`

<br>

> `[PUT]` /schedules/{schedule_id}<br>
> Replaces the specified schedule with a new schedule which follows the `Schedule Structure`

<br>

> `[GET]` /schedules/active<br>
> Gets the currently running schedule

<br>

> `[PUT]` /schedules/active/{schedule_id}<br>
> Sets the specified schedule as active (disabled previously active schedule)

<br>

> `[DELETE]` /schedules/active/{schedule_id}<br>
> Disables the specified schedule if it was active