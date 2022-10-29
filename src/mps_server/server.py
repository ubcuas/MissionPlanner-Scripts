import math
import socketserver

from src.mps_server.missions import Mission
from src.common.wpqueue import Waypoint, WaypointQueue
from src.common.sharedobject import SharedObject

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
        current_hdg = str(parameters[3]).strip(' b\'')
        current_vel = str(parameters[4]).strip(' b\'')

        print(f"Current Location: lat: {current_lat} lng: {current_lng} alt: {current_alt}")
        print(f"                  hdg: {current_hdg} vel: {current_vel}")
        current_wp = Waypoint("", current_lat, current_lng, current_alt)

        #updated shared obj with location data
        self.server._so.mps_status_set({"velocity":current_vel, "latitude":current_lat, "longitude":current_lng, "altitude":current_alt, "heading":current_hdg})

        #send instruction to UAV
        socket.sendto(bytes(self.next_instruction(current_wp), "utf-8"), self.client_address)
    
    def next_instruction(self, current_wp):
        instruction = "IDLE 0 0 0" #default instr is to idle

        #check if we should lock
        if self.server._so.mps_locked_get():
            print("Locking")
            if self.server._locked:
                #still locked, idle
                pass
            else:
                #tell the UAV to remove the current waypoint
                instruction = "LOCK 1 0 0"
                self.server._locked = True
        else:
            #reset _locked if coming out of locked state
            if self.server._locked:
                self.server._locked = False

            #check for a new mission
            nextwpq = self.server._so.mps_newmission_get()
            if nextwpq != None: 
                #overwrite the current mission with the new one
                print("New Mission Found!")
                self.server._current_mission = Mission(nextwpq)
                #IDLE instruction
            else:
                #check if current mission has completed
                if (self.server._current_mission.mission_complete()):
                    print("Idling...")
                    #IDLE instruction
                else:
                    #check progress
                    if (self.server._current_mission.mission_check_wp(current_wp)):
                        print("Waypoint Reached!")
                        #IDLE instruction

                    #send waypoint to UAV
                    if (self.server._current_mission.mission_complete()):
                        print("Mission Complete!")
                        #IDLE instruction
                    else:
                        print("NEXT")
                        #send the next waypoint to the UAV
                        instruction = "NEXT " + str(self.server._current_mission.mission_current_wp())
        
        return instruction
            

class MPS_Internal_Server(socketserver.UDPServer):
    def __init__(self, hptuple, handler, so):
        self._so = so

        self._current_mission = Mission() #empty mission

        self._locked = False

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

    server = MPS_Server(testobj)
    server.serve_forever()
