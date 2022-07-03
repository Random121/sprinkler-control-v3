# sprinkler-control-v3

## TODO
1. Extend jsonschema validator to include custom error messages
2. implement front end in Vue or React


## HTTP API

> GET http://192.168.0.27:42488/v1/api/sprinklers/

Retrieve information of all sprinklers.

<br>

> POST REQUEST BODY
```
{
	"action_name": "NAME OF ACTION HERE",
	"arguments": {
		"relay_id": "OPTIONAL DEPENDING ON THE REQUEST",
		"duration": "DURATION OF RELAY IN SECONDS"
	}
}
```

<br>

> POST http://192.168.0.27:42488/v1/api/sprinklers/\<relay_id\>

Perform action on the specified sprinkler (relay_id). relay_id of a sprinkler
is shown on the buttons of the web interface.

<br>

> POST http://192.168.0.27:42488/v1/api/sprinklers/

Performs the same thing as the previous post request except the relay_id can
be specified in the arguments section of the request.

## NOTE
The regexp for 24 hour time specified in "schedule.schema.json" is a modification of the regexp from [this site](https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s06.html) to make the seconds optional