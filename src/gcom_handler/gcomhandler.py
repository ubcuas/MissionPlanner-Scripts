from http.server import HTTPServer, BaseHTTPRequestHandler
import time
from ..mps_server.missions import Mission
from ..common.wpqueue import WaypointQueue, Waypoint
from ..common.sharedobject import SharedObject

WpQueue1 = WaypointQueue([Waypoint(-35.3627798, 149.1651830, 10), Waypoint(-35.3631439, 149.1647033, 10), Waypoint(-35.3637428, 149.1647949, 10), Waypoint(-35.3638713, 149.1659743, 10)])
WpQueue2 = WaypointQueue([Waypoint(-35.3687798, 149.1651830, 10), Waypoint(-35.3691439, 149.1647033, 10), Waypoint(-35.3697428, 149.1647949, 10), Waypoint(-35.3698713, 149.1659743, 10)])

queue = [WpQueue1,WpQueue2]


class GCom_Handler(BaseHTTPRequestHandler):
    pass 
    # def so_push(self):
    #     for q in self.queue:
    #         while(self._so.gcom_newmission_set(self, q) == False):
    #             pass


class GCom_Server(BaseHTTPRequestHandler):
    def __init__(self, so):
        self._so = so
        pass

    def serve_forever(self):
        for q in queue:
            while(self._so.gcom_newmission_set(self, q) == False):
                pass
    
        # PORT = 9000
        # server = HTTPServer(('', PORT), GCom_Handler)
        # print("Server running on port %s" % PORT)
        # server.serve_forever()



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




