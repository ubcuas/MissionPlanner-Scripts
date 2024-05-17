import time
import json
import socketio

from server.common.sharedobject import SharedObject
from server.common.status import Status

class Status_Client():
    def __init__(self, shared_obj: SharedObject):
        self._so: SharedObject = shared_obj
        self._url: str = ""
        self._delay = 1

    def get_status_json(self) -> str:
        return json.dumps(self._so.get_status().as_dictionary())
    
    def handle_error(self, data):
        print(f"Error sending status data: {data}")
    
    def connect_to(self, production: bool, host: str, port: int):
        print("Status Websocket Client starting...")
        self._url = f"ws://{host}:{port}/socket.io/"

        self.sio = socketio.SimpleClient()

        self.sio.connect(self._url)
        self.sio.on('pong', )
        self.sio.on('error', self.handle_error)

        while True:
            try:
                self.sio.call("ping", timeout=60)
                break
            except TimeoutError:
                #ping was not returned, cycle again
                pass

        while True:
            self.sio.emit('drone_update', self.get_status_json())
            time.sleep(self._delay)