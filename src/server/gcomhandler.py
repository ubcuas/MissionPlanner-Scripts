import wsgiserver
from flask import Flask, jsonify, request
import json

from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.sharedobject import SharedObject

class GCom_Server():
    def __init__(self, so):
        self._so = so

        print("GCom_Server Initialized")

    def serve_forever(self, production=True, HOST="localhost", PORT=9000):
        app = Flask(__name__)

        production_server = wsgiserver.WSGIServer(app, host=HOST, port=PORT)

        #GET endpoints

        @app.route("/queue", methods=["GET"])
        def get_queue():
            ret = self._so.gcom_currentmission_get() # this is a dict of wpq (hopefully)
            formatted = []
            for wp in ret:
                formatted.append(wp.get_asdict())
            retJSON = json.dumps(formatted) # this should convert the dict to JSON

            print("Queue sent to GCom")

            return retJSON

        @app.route("/status", methods=["GET"])
        def get_status():
            ret = self._so.gcom_status_get() # this should be a dict of status (hopefully)
            retJSON = json.dumps(ret) # this should convert the dict to JSON

            print("Status sent to GCom")

            return retJSON

        @app.route("/lock", methods=["GET"])
        def lock():
            status = self._so.gcom_locked_set(True)
            if status:
                print("Locked by GCom")
                return "Mission Queue Locked"

            else:
                print("Lock failed")

                return "Mission Queue Lock Error: Already Locked", 400


        @app.route("/unlock", methods=["GET"])
        def unlock():
            status = self._so.gcom_locked_set(False)
            if status:
                print("unlocked by GCom")

                return "Mission Queue unlocked"
            else:
                print("Unlock failed")

                return "Mission Queue Unlock Error: Already Unlocked", 400


        @app.route("/rtl", methods=["GET"])
        def rtl():
            print("RTL")
            self._so.gcom_rtl_set(True)

            return "Returning to Land"

        @app.route("/land", methods=["GET"])
        def land():
            print("Landing")
            self._so.gcom_landing_set(True)

            return "Landing in Place"

        #POST endpoints

        @app.route("/queue", methods=["POST"])
        def post_queue():
            payload = request.get_json()

            ret = self._so.gcom_status_get()
            last_altitude = ret['altitude'] if ret != () else 50

            wpq = []
            for wpdict in payload:
                if wpdict['altitude'] != None:
                    wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], wpdict['altitude'])
                    wpq.append(wp)
                    last_altitude = wpdict['altitude']
                else:
                    wp = Waypoint(wpdict['id'], wpdict['name'], wpdict['latitude'], wpdict['longitude'], last_altitude)
                    wpq.append(wp)
            
            self._so.gcom_newmission_set(WaypointQueue(wpq.copy()))

            wpq.clear()

            return "ok"
    
        @app.route("/takeoff", methods=["POST"])
        def takeoff():
            payload = request.get_json()

            if not('altitude' in payload):
                return "Altitude cannot be null", 400

            altitude = int(payload['altitude'])
            print(f"Taking off to altitude {altitude}")
            self._so.gcom_takeoffalt_set(altitude)

            return "Takeoff command received"

        @app.route("/home", methods=["POST"])
        def home():
            home = request.get_json()

            if 'longitude' not in home or 'latitude' not in home or 'altitude' not in home:
                return "Long/lat/alt cannot be null", 400

            self._so.gcom_newhome_set(home)

            return "Setting New Home"
        
        #VTOL endpoints
        @app.route("/vtol/transition", methods=["GET", "POST"])
        def vtol_transition():
            if request.method == "GET":
                ret = self._so.mps_vtol_get()
                return ret
            elif request.method == "POST":
                payload = request.get_json()
                mode = int(payload['mode'])
                self._so.gcom_vtol_set(mode)
                return "Changing flight mode"

        #Fence inclusion/exclusion methods...

        @app.route("/fence/inclusive", methods=["POST"])
        def fence_inclusive():
            fence = request.get_json()

            self._so.gcom_fence_set({"inex":False, "type":"circle", "center":fence['center'], "radius":fence['radius']})

            return "Inclusive Fence Set"
        
        @app.route("/fence/exclusive", methods=["POST"])
        def fence_exclusive():
            fence = request.get_json()

            self._so.gcom_fence_set({"inex":True, "type":"circle", "center":fence['center'], "radius":fence['radius']})

            return "Exclusive Fence Set"
        
        #end of endpoints

        #run server
        if production:
            production_server.start()
        else:
            app.run(port=PORT)
