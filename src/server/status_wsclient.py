import time
import socketio

from server.common.sharedobject import SharedObject
from server.common.status import Status

DELAY = 1
RECONNECT = 15

class Status_Client():
    def __init__(self, shared_obj: SharedObject):
        self._so: SharedObject = shared_obj
        self._url: str = ""
    
    def handle_error(self, data):
        print(f"Error sending status data: {data}")
    
    def connect_to(self, production: bool, host: str, port: int):
        print("Status Websocket Client starting...")
        self._url = f"ws://{host}:{port}"

        self.sio = socketio.Client()
        self.sio.on('error', self.handle_error)

        while True:
            try:
                self.sio.connect(self._url)
                break
            except:
                print(f"Status Websocket Client: Connection failed, retrying in {RECONNECT} second(s)")

        while True:
            self.sio.emit('drone_update', self._so.get_status().as_reduced_status())
            time.sleep(DELAY)
            #A BadNamespaceError will occur when GCOM disconnects suddenly - leverage this for a reconnect?