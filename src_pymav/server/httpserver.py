from flask import Flask, request
import json
from flask_socketio import SocketIO

from server.operations.takeoff import takeoff

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
        def endpoint_takeoff():
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
        
        socketio.run(app, host='0.0.0.0', port=PORT, debug=True, use_reloader=False)