import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from src.common.wpqueue import WaypointQueue, Waypoint
from src.common.sharedobject import SharedObject

#define handler
class GCom_Handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # self.send_response(200)
        # self.send_header('content-type', 'text/html')
        # self.end_headers()

        # output = "alive"
        # self.wfile.write(output.encode())

        if self.path.endswith('/queue'):
            ret = self.server._so.gcom_currentmission_get() # this is a dict of wpq (hopefully)
            formatted = []
            for wp in ret:
                formatted.append(wp.get_asdict())
            retJSON = json.dumps(formatted) # this should convert the dict to JSON

            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            self.wfile.write(retJSON.encode())

            print("Queue sent to GCom")

        elif self.path.endswith('/status'):
            ret = self.server._so.gcom_status_get() # this should be a dict of status (hopefully)
            retJSON = json.dumps(ret) # this should convert the dict to JSON

            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            self.wfile.write(retJSON.encode())

            print("Status sent to GCom")

        elif self.path.endswith('/lock'):
            status = self.server._so.gcom_locked_set(True)
            if status:
                print("Locked by GCom")

                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = "Mission Queue Locked"
                self.wfile.write(output.encode())
            else:
                print("Lock failed")

                self.send_response(400)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = "Mission Queue Lock Error: Already Locked"
                self.wfile.write(output.encode())

        elif self.path.endswith('/unlock'):
            status = self.server._so.gcom_locked_set(False)
            if status:
                print("unlocked by GCom")

                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = "Mission Queue unlocked"
                self.wfile.write(output.encode())
            else:
                print("Unlock failed")

                self.send_response(400)
                self.send_header('content-type', 'text/html')
                self.end_headers()

                output = "Mission Queue Unlock Error: Already Unlocked"
                self.wfile.write(output.encode())
        
        elif "/takeoff/" in self.path:
            params = self.path.split("/takeoff/")
            altitude = int(params[1])
            print(f"Taking off to altitude {altitude}")
            self.server._so.gcom_takeoffalt_set(altitude)


    def do_POST(self):
        if self.path.endswith('/queue'):
            content_len = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_len)
            post_data = post_body.decode('utf-8')
            payload = json.loads(post_data)

            ret = self.server._so.gcom_status_get()
            last_altitude = ret['altitude'] if ret != () else 50

            wpq = []
            for wpdict in payload:
                if wpdict['altitude'] != None:
                    wp = Waypoint(wpdict['name'], wpdict['latitude'], wpdict['longitude'], wpdict['altitude'])
                    wpq.append(wp)
                    last_altitude = wpdict['altitude']
                else:
                    wp = Waypoint(wpdict['name'], wpdict['latitude'], wpdict['longitude'], last_altitude)
                    wpq.append(wp)
            
            self.server._so.gcom_newmission_set(WaypointQueue(wpq.copy()))

            wpq.clear()

            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()

            output = "ok"
            self.wfile.write(output.encode())


class GCom_Internal_Server(HTTPServer):
    def __init__(self, hptuple, handler, so):
        self._so = so

        #superclass constructor
        super().__init__(hptuple, handler)
        print("GCom_Internal_Server initialized")

class GCom_Server():
    def __init__(self, so):
        self._so = so

        print("GCom_Server Initialized")

    def serve_forever(self):
        HOST, PORT = "localhost", 9000
        server = GCom_Internal_Server((HOST, PORT), GCom_Handler, self._so)
        server.serve_forever()

        # for q in queue:
        #     while(self._so.gcom_newmission_set(q) == False):
        #         time.sleep(0.1)
        #     print("Mission added")

if __name__ == "__main__":
    testobj = SharedObject()

    server = GCom_Server(testobj)
    server.serve_forever()
