from flask import Flask, request
from flask_socketio import SocketIO, send, emit
from server.common.conversion import *
import time
import json

from server.common.wpqueue import WaypointQueue, Waypoint

class Socket_Handler():
    def __init__(self, so):
        self.so = so
        print("SocketHandler Initialized")

    def serve_forever(self, production=True, HOST="localhost", PORT=9001):
        app = Flask(__name__)
        socketio = SocketIO(app, logger=True)

        @app.route("/test")
        def test():
            return "Socket is running"
        
        @socketio.on('connect')
        def handle_connect():
            print("Client connected to socket")

        @socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected")

        @socketio.on('message')
        def handle_message(msg):
            #print(f'Message received: {msg}')
            ret = self.so.gcom_status_get()
            retJSON = json.dumps(ret)
            emit('message', {'status_data': retJSON})
        
        socketio.run(app, host=HOST, port=PORT, debug=True, use_reloader=False)
