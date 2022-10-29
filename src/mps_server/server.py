import math
import socketserver

from src.mps_server.missions import Mission
from src.common.wpqueue import Waypoint, WaypointQueue
from src.common.sharedobject import SharedObject

#create a test mission
wpq1 = WaypointQueue([
    Waypoint(-35.3627798, 149.1651830, 10),
    Waypoint(-35.3631439, 149.1647033, 10),
    Waypoint(-35.3637428, 149.1647949, 10),
    Waypoint(-35.3638713, 149.1659743, 10)
])
first_mission = Mission(wpq1)

wpq2 = WaypointQueue([
    Waypoint(-35.3647798, 149.1651830, 10),
    Waypoint(-35.3651439, 149.1647033, 10),
    Waypoint(-35.3657428, 149.1647949, 10),
    Waypoint(-35.3658713, 149.1659743, 10)
])

#define request handler
class MPS_Handler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        #receive location data
        data = self.request[0].strip()
        socket = self.request[1]

        parameters = data.split()
        current_lat = str(parameters[0]).strip(' b\'')
        current_lng = str(parameters[1]).strip(' b\'')
        current_alt = str(parameters[2]).strip(' b\'')

        print(f"Current Location: lat: {current_lat} lng: {current_lng} alt: {current_alt}")
        current_wp = Waypoint(current_lat, current_lng, current_alt)

        #check if current mission has completed
        if (self.server._current_mission.mission_complete()):
            socket.sendto(bytes("IDLE 0 0 0", "utf-8"), self.client_address)
            print("Idling...")
            #check for a new mission
            nextwpq = self.server._so.mps_newmission_get()
            if nextwpq != None:
                print("New Mission Found!")
                self.server._current_mission = Mission(nextwpq) #TODO overwrite the queue instead
        else:
            #check progress
            if (self.server._current_mission.mission_check_wp(current_wp)):
                print("Waypoint Reached!")

            #send waypoint to UAV
            if (self.server._current_mission.mission_complete()):
                print("Mission Complete!")
                socket.sendto(bytes("IDLE 0 0 0", "utf-8"), self.client_address)
            else:
                #send the next waypoint to the UAV
                socket.sendto(bytes("NEXT " + str(self.server._current_mission.mission_current_wp()), "utf-8"), self.client_address)

class MPS_Internal_Server(socketserver.UDPServer):
    def __init__(self, hptuple, handler, so):
        self._so = so

        self._current_mission = Mission() #empty mission

        #superclass constructor
        super().__init__(hptuple, handler)
        print("MPS_Internal_Server initialized")

class MPS_Server():
    def __init__(self, so):
        self._so = so

        print("MPS_Server initialized")

    def serve_forever(self):
        HOST, PORT = "localhost", 4000
        self._server = MPS_Internal_Server((HOST, PORT), MPS_Handler, self._so)
        self._server.serve_forever()

if __name__ == "__main__":
    testobj = SharedObject()
    while(testobj.gcom_newmission_set(wpq2) == False):
        pass

    server = MPS_Server(testobj)
    server.serve_forever()
