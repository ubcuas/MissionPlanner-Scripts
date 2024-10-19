from flask import Flask, request
import json
from flask_socketio import SocketIO

from server.operations.takeoff import takeoff
from server.operations.queue import new_mission

from server.common.conversion import *
from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.status import Status
from server.common.encoders import command_string_to_int, command_int_to_string

class HTTP_Server():
    def __init__(self, mav_connection):
        self.mav_connection = mav_connection

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
            #TODO: notes for refactor
            # works by reading the entire queue, and also reading
            # the current waypoint we are on (a part of status)
            # returns only the waypoints we have left in the mission,
            # not the ones already traveled to
            
            # self._so.gcom_currentmission_trigger_update()
            # while self._so._currentmission_flg_ready == False:
            #     #time.sleep(0.01)
            #     pass

            # ret = self._so.gcom_currentmission_get() # This is a dict of wpq (hopefully)
            # formatted = []
            # for wp in ret:
            #     wp_dict = wp.get_asdict()
            #     wp_dict.update(wp.get_command())
            #     formatted.append(wp_dict)
            
            # wpno = int(self._so.get_status()._wpn)
            # remaining = formatted[wpno-1:]
            # retJSON = json.dumps(remaining) # This should convert the dict to JSON

            # print("Queue sent to GCOM")

            return "", 200
        
        @app.route("/queue", methods=["POST"])
        def post_queue():
            payload = request.get_json()

            #ret: Status = self._so.get_status() TODO replace with status call
            ret = {}
            last_altitude = ret.get("alt", 50)

            wpq = []
            for wpdict in payload:
                altitude = wpdict.get('altitude')
                if altitude != None:
                    last_altitude = altitude
                else:
                    altitude = last_altitude

                command = wpdict.get('command', "WAYPOINT") 
                # converts any unknown waypoint types to WAYPOINT
                command = command_int_to_string(command_string_to_int(command))

                param1 = wpdict.get('param1', 0)
                param2 = wpdict.get('param2', 0)
                param3 = wpdict.get('param3', 0)
                param4 = wpdict.get('param4', 0)
                
                wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], last_altitude, 
                              command, param1, param2, param3, param4)
                wpq.append(wp)
            
            new_mission(self.mav_connection, WaypointQueue(wpq.copy()))
            copy = WaypointQueue(wpq.copy()).aslist()
            wpq.clear()

            return "ok", 200
        
        @app.route("/insert", methods=['POST'])
        def post_insert_wp():
            payload = request.get_json()

            ret: Status = self._so.get_status()
            last_altitude = ret._alt if ret != () else 50

            # gets new waypoints
            new_waypoints = []
            for wpdict in payload:
                altitude = wpdict.get('altitude')
                if altitude != None:
                    last_altitude = altitude
                else:
                    altitude = last_altitude

                command = wpdict.get('command', "WAYPOINT") 
                # converts any unknown waypoint types to WAYPOINT
                command = command_int_to_string(command_string_to_int(command))

                param1 = wpdict.get('param1', 0)
                param2 = wpdict.get('param2', 0)
                param3 = wpdict.get('param3', 0)
                param4 = wpdict.get('param4', 0)
                
                wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], last_altitude, 
                              command, param1, param2, param3, param4)
                new_waypoints.append(wp)
            
            # insert new waypoints start at index
            new_mission(self.mav_connection, WaypointQueue(new_waypoints.copy()))
            copy = WaypointQueue(new_waypoints.copy()).aslist()
            new_waypoints.clear()

            return "Waypoint Inserted", 200
        
        @app.route("/clear", methods=['GET'])
        def get_clear_queue():
            new_mission(self.mav_connection, WaypointQueue([]))

            return "Mission has been Cleared", 200
                
        @app.route("/status", methods=["GET"])
        def get_status():
            #TODO: ensure that the status has all the fields
            # ret: Status = self._so.get_status()
            # retJSON = json.dumps(ret.as_dictionary())

            # print("Status sent to GCOM")

            return "", 200
        
        @app.route("/takeoff", methods=["POST"])
        def post_takeoff():
            payload = request.get_json()

            if not('altitude' in payload):
                return "Altitude cannot be null", 400

            altitude = int(payload['altitude'])
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

            if input['arm'] in [1, 0]:
                print(f"arming {int(input['arm'])}")
                # self._so.arm_set(int(input['arm']))

                # result = None
                # while result == None:
                #     result = self._so.arm_get_result()
                #     time.sleep(0.05)
                result = 0 # TODO change to arm operation call
                if result == 1:
                    return f"OK! {'Armed drone' if input['arm'] else 'Disarmed drone'}", 200
                else:
                    return f"Arm/disarm failed - drone is NOT in the requested state", 418
            else:
                return f"Unrecognized arm/disarm command parameter", 400

        @app.route("/rtl", methods=["GET", "POST"])
        def get_post_rtl():
            altitude = request.get_json().get('altitude', 50)

            print(f"RTL at {altitude}")
            #self._so.gcom_rtl_set(altitude) #TODO call into RTL operation

            return "Returning to Launch", 200
        
        @app.route("/land", methods=["GET"])
        def get_land():
            print("Landing")
            # self._so.flightmode_set("loiter")
            # self._so.gcom_landing_set(True) #TODO replace with landing procedure
            return "Landing Immediately", 200

        @app.route("/land", methods=["POST"])
        def post_land():
            land = request.get_json()
            if not 'latitude' in land or not 'longitude' in land:
                return "Latitude and Longitude cannot be null", 400
            
            #self._so.land_at_pos_set(land) #TODO call into landing procedure

            return "Landing at Specified Location", 200
        
        @app.route("/home", methods=["POST"])
        def post_home():
            home = request.get_json()

            if 'longitude' not in home or 'latitude' not in home or 'altitude' not in home:
                return "Long/lat/alt cannot be null", 400

            # #self._so.gcom_newhome_set(home) TODO call into set new home operation

            return "Setting New Home", 200
        
        @app.route("/flightmode", methods=["PUT"])
        def put_flight_mode():
            input = request.get_json()
            
            if input['mode'] in ['loiter', 'stabilize', 'auto', 'guided']:
                #self._so.flightmode_set(input['mode']) # TODO call into operation
                return f"OK! Changed mode: {input['mode']}", 200
            elif input['mode'] in ['copter', 'plane']:
                print("changing mode")
                #self._so.flightConfig_set(input['mode']) # TODO call into operation
                return f"OK! Changed mode: {input['mode']}", 200
            else:
                return f"Unrecognized mode: {input['mode']}", 400
        
        socketio.run(app, host='0.0.0.0', port=PORT, debug=True, use_reloader=False)