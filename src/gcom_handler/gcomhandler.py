import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

from src.common.wpqueue import WaypointQueue, Waypoint
from src.common.sharedobject import SharedObject

wpq1 = WaypointQueue([
    Waypoint(-35.3627798, 149.1651830, 10),
    Waypoint(-35.3631439, 149.1647033, 10),
    Waypoint(-35.3637428, 149.1647949, 10),
    Waypoint(-35.3638713, 149.1659743, 10)
])

wpq2 = WaypointQueue([
    Waypoint(-35.3647798, 149.1651830, 10),
    Waypoint(-35.3651439, 149.1647033, 10),
    Waypoint(-35.3657428, 149.1647949, 10),
    Waypoint(-35.3658713, 149.1659743, 10)
])

queue = [wpq1, wpq2]

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


    def do_POST(self):
        if self.path.endswith('/queue'):
            content_len = int(self.headers['Content-Length'])
            post_body = self.rfile.read(content_len)
            post_data = post_body.decode('utf-8')
            payload = json.loads(post_data)

            wpq = []
            for wpdict in payload:
                wp = Waypoint(wpdict['latitude'], wpdict['longitude'], wpdict['altitude'])
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

"""
class GComHandler(BaseHTTPRequestHandler):
    queue = [[1000, 200, 350],[5000, 230, 450],[500, 120, 250]]
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        output = ''
        output += "<html><body>"
        output += "<h1>WayPoints</h1>"

        for task in self.queue:
            for terms in task:
                output += str(terms) + " "

            output += "</br>"
        
        output += "</body></html>"
        self.wfile.write(output.encode())

        def run():
            PORT = 9000
            server = HTTPServer(('', PORT), GComHandler)
            print("Server running on port %s" % PORT)
            server.serve_forever()


        if __name__ == "__main__":
            run()

"""




