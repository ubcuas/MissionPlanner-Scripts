from flask import Flask, jsonify, request
import json

from src.common.wpqueue import WaypointQueue, Waypoint
from src.common.sharedobject import SharedObject

class GCom_Server():
    def __init__(self, so):
        self._so = so

        print("GCom_Server Initialized")

    def serve_forever(self):
        HOST, PORT = "localhost", 9000
        app = Flask(__name__)

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

                return "Mission Queue Lock Error: Already Locked"


        @app.route("/unlock", methods=["GET"])
        def unlock():
            status = self._so.gcom_locked_set(False)
            if status:
                print("unlocked by GCom")

                return "Mission Queue unlocked"
            else:
                print("Unlock failed")

                return "Mission Queue Unlock Error: Already Unlocked"


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

            altitude = int(payload['altitude'])
            print(f"Taking off to altitude {altitude}")
            self._so.gcom_takeoffalt_set(altitude)

            return "Takeoff command received"

        @app.route("/home", methods=["POST"])
        def home():
            home = request.get_json()

            self._so.gcom_newhome_set(home)

            return "Setting New Home"
        
        #end of endpoints

        #run server
        app.run(port=PORT)
