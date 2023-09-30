from flask import Flask, request
from flask_socketio import SocketIO
from server.common.conversion import *
import time
import json

from server.common.wpqueue import WaypointQueue, Waypoint

class Socket_Handler():
    def __init__(self, so):
        self.so = so
        print("SocketHandler Initialized")

    def serve_forever(self, production=True, HOST="localhost", PORT=5050):
        app = Flask(__name__)
        socketio = SocketIO(app)

        @app.route("/test")
        def test():
            return "Socket is running"
        
        @socketio.on('connect')
        def handle_connect():
            print("Client connected to socket")
            socketio.emit('okay', {'data': 'Connected'})

        @socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected")

        @socketio.on('message')
        def handle_message():
            ret = self.so.gcom_status_get()
            retJSON = json.dumps(ret)
            print("Status sent to GCOM")
            socketio.emit('status_response', {'status_data': retJSON})
        
        socketio.run(app, host=HOST, port=PORT, debug=True, use_reloader=False)
