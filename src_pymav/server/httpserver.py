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
from server.features.camera import configure_camera, trigger_camera

from server.utilities.request_message_streaming import set_parameter

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

            curr = max(ret._wpn, 1)
            curr_wpq = get_current_mission(self.mav_connection)

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
            
            # start list with new waypoints, extend with current mission at the end
            new_waypoints.extend(curr_wpq.aslist()[curr:])

            success = new_mission(self.mav_connection, WaypointQueue(new_waypoints.copy()))
            copy = WaypointQueue(new_waypoints.copy()).aslist()
            new_waypoints.clear()
            
            if success:
                return "Waypoint(s) Inserted", 200
            else:
                return "Failed to set new mission", 400

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
            if request.method == "GET":
                altitude = 50
            else:
                altitude = request.get_json().get("altitude", 50)

            print(f"RTL at {altitude}")

            # set RTL altitude parameter
            alt_cm = altitude * 100

            if not set_parameter(self.mav_connection, "RTL_ALT", alt_cm):
                return "Failed to set RTL altitude parameter", 400

            success = change_flight_mode(
                self.mav_connection,
                self.mav_connection.target_system,
                self.mav_connection.target_component,
                "RTL",
            )

            if success:
                return "Returning to Launch", 200
            else:
                return "Failed to RTL", 400

        @app.route("/land", methods=["GET"])
        def get_land():
            print("Landing")
            if not change_flight_mode(self.mav_connection, "LOITER"):
                return "Failed to set drone into LOITER mode", 400

            if land_in_place(self.mav_connection) == 0:
                return "Landing Immediately", 200
            else:
                return "Landing failed", 400

        @app.route("/land", methods=["POST"])
        def post_land():
            # land_at_position does not seem to work for a copter
            # land_at_position(self.mav_connection, land.get("latitude"), land.get("longitude")) == 0:

            land = request.get_json()
            if "latitude" not in land or "longitude" not in land:
                return "Latitude and Longitude cannot be null", 400
            
            landing_mission = WaypointQueue()
            landing_mission.push(Waypoint(0, "Approach", land.get('latitude'), land.get('longitude'), land.get('altitude', 35)))
            landing_mission.push(Waypoint(1, "Landing", land.get('latitude'), land.get('longitude'), 0, "LAND"))

            if new_mission(self.mav_connection, landing_mission):
                return "Landing at Specified Location", 200
            else:
                return "Landing failed", 400

        @app.route("/home", methods=["POST"])
        def post_home():
            home: dict = request.get_json()

            if (
                "longitude" not in home
                or "latitude" not in home
                or "altitude" not in home
            ):
                return "Long/lat/alt cannot be null", 400

            if set_home(self.mav_connection, home.get("latitude"), home.get("longitude"), home.get("altitude")) == 0:
                return "Setting New Home", 200
            else:
                return "New Home NOT set", 400

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
                
                if new_mission(self.mav_connection, wpq):
                    return f"Scan Mission Set", 200
                else:
                    return "Mission request failed", 400
            else:
                return f"Invalid input, missing a parameter.", 400
            
        @app.route("/camera/immediate_trigger", methods=["GET"])
        def camera_immediate_trigger():
            if configure_camera(self.mav_connection, "IMMEDIATE", trigger_time=0, trigger_dist=0) != 0:
                return "Failed to configure camera", 400
            
            if trigger_camera(self.mav_connection, enable=1) != 0:
                return "Failed to trigger camera", 400
                
            return "Successfully triggered camera once", 200
        
        @app.route("/camera/sustained_trigger", methods=["POST"])
        def camera_sustained_trigger():
            input = request.get_json()
            if input["trigger_mode"] == "INTERVAL":
                result = configure_camera(self.mav_connection, "INTERVAL", trigger_time=input["trigger_cycle_time"], trigger_dist=0)
            elif input["trigger_mode"] == "DIST":
                result = configure_camera(self.mav_connection, "DIST", trigger_time=0, trigger_dist=input["trigger_distance"])
            else:
                return "Invalid trigger mode", 400
            
            if result != 0:
                return "Failed to configure camera", 400
            
            if trigger_camera(self.mav_connection, enable=1) != 0:
                return "Failed to trigger camera", 400
                
            return "Successfully started sustained triggering", 200

        socketio.run(app, host="0.0.0.0", port=PORT, debug=True, use_reloader=False)
