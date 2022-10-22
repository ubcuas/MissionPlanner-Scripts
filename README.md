# MissionPlanner Scripts

# Endpoints
## (GET) /queue
Returns the current list of waypoints in the queue, in the order of their names. GCOM stores longitudes and latitudes internally, so we really only need the order of names of waypoints.

Waypoints that have been passed and removed from the queue, obviously, should not be displayed here either.

Example response body:
```
{
    "queue": [
        {
            "name": "Alpha",
            "longitude": 38.83731,
            "latitude": -20.48321,
            "altitude": 50.7
        },
        {
            "name": "Beta",
            "longitude": 38.83731,
            "latitude": -20.48321,
            "altitude": 50.7
        }
    ]
}
```

## (POST) /queue
POST request containing a list of waypoints with names and longitude, latitude, and altitude values. If altitude is nil, carry on with the same altitude as you had last waypoint.

Previous queue should be overwritten if there is already one in place.

Longitude, name, and latitude must not be null/empty. Returns a Bad Request status code and error message in that case.
Longitude and latitude in degrees, altitude in meters.
Return status code 200 if successfully POSTed.

Example request body:
```
{
    "queue": [
        {
            "name": "Alpha",
            "longitude": 38.83731,
            "latitude": -20.48321,
            "altitude": 50.7
        },
        {
            "name": "Beta",
            "longitude": 38.83731,
            "latitude": -20.48321,
            "altitude": null
        }
    ]
}
```

## (GET) /status
GET request returns the aircraft status.
Velocity in m/s. Altitude in meters. Longitude, latitude, heading in degrees.

Example response:
```
{
    "velocity": 22.2,
    "longitude": 38.3182,
    "latitude":  82.111,
    "altitude": 28.1111,
    "heading": 11.2
}
```

## (GET) /lock
Stops the aircraft from moving based on the Mission Planner scripts' waypoint queue loading functionality, maintaining the queue internally.
Return Bad Request if the aircraft is already locked,
or the queue is empty.

It is still be possible to run (POST) /queue while the aircraft is locked.

This won't literally lock the aircraft either, i.e.
we can still manually set waypoints with Mission Planner. This just pauses the loading functionality of the queue program. If currently moving toward a waypoint, stop moving toward it by removing it.
## (GET) /unlock
Resume moving the aircraft based on the currently stored queue. Returns a Bad Request status code and an error message if the aircraft is already unlocked.