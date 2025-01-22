import json
from flask import Flask, request
from flask_socketio import SocketIO

from pymavlink.mavutil import mavfile

from server.operations.takeoff import takeoff, arm_disarm
from server.operations.queue import new_mission, set_home, clear_mission
from server.operations.get_info import get_status, get_current_mission
from server.operations.change_modes import change_flight_mode
from server.operations.land import land_in_place, land_at_position

from server.features.aeac_scan import scan_area

from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.status import Status
from server.common.encoders import command_string_to_int, command_int_to_string


class HTTP_Server:
    def __init__(self, mav_connection):
        self.mav_connection: mavfile = mav_connection

    def serve_forever(self, production=True, HOST="localhost", PORT=9000):
        print("GCOM HTTP Server starting...")
        app = Flask(__name__)
        socketio = SocketIO(app)

        # GET endpoints
        @app.route("/", methods=["GET"])
        def index():
            return "Server Running", 200

        @app.route("/queue", methods=["GET"])
        def get_queue():
            curr = get_status(self.mav_connection)._wpn 
            wpq = get_current_mission(self.mav_connection)

            formatted = []
            for wp in wpq:
                wp_dict = wp.get_asdict()
                wp_dict.update(wp.get_command())

                formatted.append(wp_dict)
            
            remaining = json.dumps(formatted[curr:])

            print("Queue sent to GCOM")

            return remaining, 200

        @app.route("/queue", methods=["POST"])
        def post_queue():
            payload = request.get_json()

            ret = get_status(self.mav_connection)
            last_altitude = ret.as_dictionary().get("altitude", 50)

            wpq = []
            for wpdict in payload:
                altitude = wpdict.get("altitude")
                if altitude != None:
                    last_altitude = altitude
                else:
                    altitude = last_altitude

                command = wpdict.get("command", "WAYPOINT")
                # converts any unknown waypoint types to WAYPOINT
                command = command_int_to_string(command_string_to_int(command))

                param1 = wpdict.get("param1", 0)
                param2 = wpdict.get("param2", 0)
                param3 = wpdict.get("param3", 0)
                param4 = wpdict.get("param4", 0)

                wp = Waypoint(
                    wpdict["id"],
                    wpdict["name"],
                    wpdict["latitude"],
                    wpdict["longitude"],
                    last_altitude,
                    command,
                    param1,
                    param2,
                    param3,
                    param4,
                )
                wpq.append(wp)

            success = new_mission(self.mav_connection, WaypointQueue(wpq.copy()))
            copy = WaypointQueue(wpq.copy()).aslist()
            wpq.clear()

            if success:
                return "ok", 200
            else:
                return "Error uploading mission", 400

        @app.route("/insert", methods=["POST"])
        def post_insert_wp():
            payload = request.get_json()

            ret: Status = get_status(self.mav_connection)
            last_altitude = ret._alt if ret != () else 50

            # gets new waypoints
            new_waypoints = []
            for wpdict in payload:
                altitude = wpdict.get("altitude")
                if altitude != None:
                    last_altitude = altitude
                else:
                    altitude = last_altitude

                command = wpdict.get("command", "WAYPOINT")
                # converts any unknown waypoint types to WAYPOINT
                command = command_int_to_string(command_string_to_int(command))

                param1 = wpdict.get("param1", 0)
                param2 = wpdict.get("param2", 0)
                param3 = wpdict.get("param3", 0)
                param4 = wpdict.get("param4", 0)

                wp = Waypoint(
                    wpdict["id"],
                    wpdict["name"],
                    wpdict["latitude"],
                    wpdict["longitude"],
                    last_altitude,
                    command,
                    param1,
                    param2,
                    param3,
                    param4,
                )
                new_waypoints.append(wp)

            # insert new waypoints start at index
            new_mission(self.mav_connection, WaypointQueue(new_waypoints.copy()))
            copy = WaypointQueue(new_waypoints.copy()).aslist()
            new_waypoints.clear()

            return "Waypoint Inserted", 200

        @app.route("/clear", methods=["GET"])
        def get_clear_queue():
            result = clear_mission(self.mav_connection)

            if result:
                return "Mission has been Cleared", 200
            else:
                return "Failed to clear mission", 400

        @app.route("/status", methods=["GET"])
        def get_status_handler():
            print("Status sent to GCOM")
            s = get_status(self.mav_connection).as_dictionary()
            return s, 200

        @app.route("/takeoff", methods=["POST"])
        def post_takeoff():
            payload = request.get_json()

            if not ("altitude" in payload):
                return "Altitude cannot be null", 400

            altitude = int(payload["altitude"])
            print(f"Taking off to altitude {altitude}")

            try:
                result = takeoff(self.mav_connection, altitude)
            except ValueError:
                result = 1

            if result == 0:
                return "Takeoff command successful", 200
            else:
                return "Takeoff unsuccessful", 400

        @app.route("/arm", methods=["PUT"])
        def put_arm_disarm_drone():
            input = request.get_json()

            if input["arm"] in [1, 0]:
                arm = bool(input['arm'])

                print("ARMING drone" if arm else "DISARMING drone")
                
                result = arm_disarm(self.mav_connection, arm)

                if result == 0:
                    return (
                        f"OK! {'Armed drone' if input['arm'] else 'Disarmed drone'}",
                        200,
                    )
                else:
                    return (
                        f"Arm/disarm failed - drone is NOT in the requested state",
                        418,
                    )
            else:
                return f"Unrecognized arm/disarm command parameter", 400

        @app.route("/rtl", methods=["GET", "POST"])
        def get_post_rtl():
            altitude = request.get_json().get("altitude", 50)

            print(f"RTL at {altitude}")
            # self._so.gcom_rtl_set(altitude) # TODO create RTL operation

            return "Returning to Launch", 200

        @app.route("/land", methods=["GET"])
        def get_land():
            print("Landing")
            change_flight_mode("LOITER")
            land_in_place(self.mav_connection)
            return "Landing Immediately", 200

        @app.route("/land", methods=["POST"])
        def post_land():
            land = request.get_json()
            if "latitude" not in land or "longitude" not in land:
                return "Latitude and Longitude cannot be null", 400

            land_at_position(self.mav_connection, land.get("latitude"), land.get("longitude"))

            return "Landing at Specified Location", 200

        @app.route("/home", methods=["POST"])
        def post_home():
            home: dict = request.get_json()

            if (
                "longitude" not in home
                or "latitude" not in home
                or "altitude" not in home
            ):
                return "Long/lat/alt cannot be null", 400

            set_home(self.mav_connection, home.get("latitude"), home.get("longitude"), home.get("altitude"))

            return "Setting New Home", 200

        @app.route("/flightmode", methods=["PUT"])
        def put_flight_mode():
            input = request.get_json()

            success = change_flight_mode(
                self.mav_connection,
                self.mav_connection.target_system,
                self.mav_connection.target_component,
                input["mode"],
            )

            if success:
                return f"OK! Changed mode: {input['mode']}", 200
            else:
                return f"Unrecognized mode: {input['mode']}", 400
            
        @app.route("/aeac_scan", methods=["POST"])
        def generate_scan_points():
            input = request.get_json()

            # TODO Trigger CameraVision system to begin scanning
            if (input["center_lat"] and input["center_lng"] and
                input["altitude"] and input["target_area_radius"]):
                wpq = scan_area(center_lat=input["center_lat"], center_lng=input["center_lng"],
                            altitude=input["altitude"], target_area_radius=input["target_area_radius"])
                new_mission(self.mav_connection, wpq)
                return f"Scan Mission Set", 200
            else:
                return f"Invalid input, missing a parameter.", 400


        socketio.run(app, host="0.0.0.0", port=PORT, debug=True, use_reloader=False)
