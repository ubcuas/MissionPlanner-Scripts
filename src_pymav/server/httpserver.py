from flask import Flask, request
import json
from flask_socketio import SocketIO

import operations
import operations.takeoff

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
        
        @app.route("/takeoff", methods=["POST"])
        def takeoff():
            payload = request.get_json()

            if not('altitude' in payload):
                return "Altitude cannot be null", 400

            altitude = int(payload['altitude'])
            print(f"Taking off to altitude {altitude}")
            
            operations.takeoff.takeoff(self.mav_connection, altitude)

            # result = None 
            # while result == None:
            #     result = self._so.takeoff_get_result()
            #     time.sleep(0.05)
            result = 1
            
            if result == 1:
                return "Takeoff command received", 200
            else:
                return "Takeoff unsuccessful", 400
        
        socketio.run(app, host='0.0.0.0', port=PORT, debug=True, use_reloader=False)