import socketserver

from src.mps_server.missions import Mission
from src.common.wpqueue import Waypoint, Queue
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
        current_btv = str(parameters[5]).strip(' b\'')
        current_wpn = str(parameters[6]).strip(' b\'')

        #print(f"Current Location: lat: {current_lat} lng: {current_lng} alt: {current_alt}")
        #print(f"                  hdg: {current_hdg} vel: {current_vel}")

        #updated shared obj with location data
        self.server._so.mps_status_set({"velocity":float(current_vel), "latitude":float(current_lat), "longitude":float(current_lng), "altitude":float(current_alt), "heading":float(current_hdg), "batteryvoltage":float(current_btv)})

        #send instruction to UAV
        socket.sendto(bytes(self.next_instruction(int(float(current_wpn))), "utf-8"), self.client_address)
    
    def next_instruction(self, current_wpn):
        #place new instructions onto the queue
        instruction = ""

        #check if there is a new home
        newhome = self.server._so.mps_newhome_get()
        if newhome != None:
            wp = Waypoint(newhome['id'], newhome['name'], newhome['latitude'], newhome['longitude'], newhome['altitude'])
            self.server._instructions.push(f"HOME {str(wp)}")

        #check takeoff altitude
        takeoffalt = self.server._so.mps_takeoffalt_get()
        if takeoffalt != 0:
            self.server._instructions.push(f"TOFF {takeoffalt}")

        #check if we should rtl
        elif self.server._so.mps_rtl_get():
            self.server._instructions.push("RTL")
        
        #check if we should land
        elif self.server._so.mps_landing_get():
            self.server._instructions.push("LAND")

        #check if we should lock
        elif self.server._so.mps_locked_get():
            print("Locking...")
            if self.server._locked:
                #still locked, idle
                #self.server._instructions.push("IDLE")
                pass
            else:
                #send the lock instruction
                self.server._instructions.push("LOCK 1")
        else:
            #reset _locked if coming out of locked state
            if self.server._locked:
                self.serve._instructions.push("LOCK 0")
                self.server._locked = False

            #check for a new fence
            nextfence = self.server._so.mps_fence_get()
            if nextfence != None:
                print("New fence found!")

                #place instructions for the new fence onto the queue
                self.server._instructions.push(f"NEWF {'EXCLUSIVE' if nextfence[1] else 'INCLUSIVE'}")
                nextfence = nextfence[0]
                while(not nextfence.empty()):
                    curr = nextfence.pop()
                    self.server._instructions.push(f"FENCE {str(curr)}")
                self.server._instructions.push("FENCE")

            #check for a new mission
            nextwpq = self.server._so.mps_newmission_get()
            if nextwpq != None:
                #overwrite the current mission with the new one
                print("New mission found!")
                self.server._current_mission = Mission(nextwpq)
                
                #place instructions for the new mission onto the queue
                self.server._instructions.push("NEWM")
                self.server._newmc = 1
                while (not nextwpq.empty()):
                    curr = nextwpq.pop()
                    self.server._instructions.push(f"NEXT {str(curr)}")
                    self.server._newmc += 1
                self.server._instructions.push("NEXT")
            else:
                #keep going and send current wpno to shared obj
                if (self.server._newmc == 0):
                    self.server._so.mps_currentmission_update(current_wpn)
                else:
                    self.server._newmc -= 1
                #self.server._instructions.push("CONT")
                pass

        #retrieve an instruction
        if (self.server._instructions.empty()):
            return "IDLE"
        else:
            instruction = self.server._instructions.pop()
            print("instruction", instruction)
            return instruction
            

class MPS_Internal_Server(socketserver.UDPServer):
    def __init__(self, hptuple, handler, so):
        self._so = so

        self._current_mission = Mission() #empty mission
        self._instructions = Queue()

        self._locked = False
        self._newmc = 0

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
