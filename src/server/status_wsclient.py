import time
import json
import websocket

from server.common.sharedobject import SharedObject
from server.common.status import Status

class Status_Client():
    def __init__(self, shared_obj: SharedObject):
        self._so: SharedObject = shared_obj
        self._url: str = ""
        self._delay = 1

    def get_status(self) -> str:
        return json.dumps(self._so.get_status().as_dictionary())

    def on_message(self, ws, message):
        time.sleep(self._delay)
        ws.send(self.get_status())
        print(message)

    def on_error(self, ws, error):
        time.sleep(self._delay)
        ws.send(self.get_status())
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(self, ws):
        print("Opened connection with status server")
        ws.send(self.get_status())

    def ping_forever(self, production: bool, host: str, port: int):
        print("Status Websocket Client starting...")
        self._url = "ws://echo.websocket.events/"#f"ws://{host}:{port}/socket.io/"

        self._ws = websocket.WebSocketApp(self._url,
                                          on_open=self.on_open,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close)
        
        self._ws.run_forever(reconnect=5)
