# MissionPlanner Scripts

## Table of Contents

1. [Instructions](#instructions)
2. [Legacy Instructions](#legacy-instructions)
3. [Endpoints](#endpoints)
4. [Sockets](#sockets)

## Instructions

### MAVProxy stuff here

## Legacy Instructions

### SITL & MissionPlanner

1. In order to run SITL on your local machine, you will need to have Docker installed. For installation instructions, refer to the
following:

    - [Windows Installation](https://docs.docker.com/desktop/install/windows-install/)
    - [MacOS Installation](https://docs.docker.com/desktop/install/mac-install/)

2. You will also need to have MissionPlanner installed on your system. Refer to installation steps [here](https://ardupilot.org/planner/docs/mission-planner-installation.html).

3. Once you have Docker, you will need to pull the [SITL image from DockerHub](https://hub.docker.com/r/ubcuas/uasitl/tags). To do this, run the Docker application then run the following command (where `X.X.X` is the desired ArduPilot version - this should match what is/will be running on the drone):

    - ArduPlane (VTOL):
        - x86: `docker pull ubcuas/uasitl:plane-X.X.X`
        - ARM64: `docker pull ubcuas/uasitl:plane-arm-X.X.X`
    - ArduCopter (Quadcopter):
        - x86: `docker pull ubcuas/uasitl:copter-X.X.X`
        - ARM64: `docker pull ubcuas/uasitl:copter-arm-X.X.X`

    If everything goes correctly, running `docker image ls` should contain an entry for `ubcuas/uasitl`.

4. Run one of the following commands to get SITL running. Refer to [the documentation](https://github.com/ubcuas/UASITL) for more customization:

    x86: `docker run --rm -d -p 5760:5760 --name acom-sitl ubcuas/uasitl:[plane/copter]-X.X.X`

    ARM64: `docker run --rm -d -p 5760:5760 --name acom-sitl ubcuas/uasitl:[plane/copter]-arm-X.X.X`

5. Next, open MissionPlanner. The first thing you will want to do is make sure that the dropdown in the top right of the UI is configured to `TCP` as shown here:

    <p align="center">
        <img src="figures/tcpdropdown.png" width="60%">
    </p>

6. Press the `Connect` Button to the right of that pane. You will be prompted with two inputs: one for hostname, and another for the remote port you want to use. Enter the following for each:

    - Hostname: `localhost`
    - Remote Port: `5760`

7. If you have completed all of the above steps you should be ready to use SITL with MissionPlanner. If you see a drone show up on the map then you should be ready to go.

### Using MissionPlanner-Scripts

> [!NOTE]
> MissionPlanner currently only works on Windows

1. Install required dependencies:

    ```c
    poetry install --no-root
    ```

2. Launch the application:

    On Windows (Powershell)
    ```
    poetry run python .\src\main.py
    ```

    On MacOS
    ```
    poetry run python src/main.py
    ```

    The server will listen on the specified port (default 9000) for HTTP requests, and will use port 4000 to communicate with MissionPlanner.

3. Start the client inside MissionPlanner:

    Navigate to the 'Scripts' tab and select `client.py` to run, the press 'Run Scripts' to start.

    <img src="figures/client_mps.png" width="60%">

### Using Tests

To run tests, you must have the Docker image running (uasitl:copter).
Then, enter the src directory and run the `pytest` command via Poetry:

```
    cd src
```

```
    poetry run pytest
```

### Command Line Arguments

| Argument | Description |
|-|-|
| `--dev` | If present, server is started in development mode rather than production. |
| `--port=9000` | Port on which to listen for HTTP requests. |
| `--status-host=localhost` | Hostname for the status socket to connect to. |
| `--status-port=1323` | Port for the status socket to connect to. |
| `--disable-status` | If present, disables the status socket. |

## Endpoints

See `api_spec.yml` or `postman_collection.json` for up-to-date information on endpoints.

## Sockets

The status WebSocket client connects to `localhost:1323` by default. The hostname and port can be changed via command-line arguments.

Every 100ms, it will emit the `drone_update` event with the following information:

```json
{
    "timestamp": 0,
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "vertical_velocity": 0.0,
    "velocity": 0.0,
    "heading": 0.0,
    "battery_voltage": 0.0
}
```

The timestamp is the number of milliseconds since the epoch.
