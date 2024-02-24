import socketserver

from server.common.missions import Mission
from server.common.wpqueue import Waypoint, Queue
from server.common.sharedobject import SharedObject

# Define request handler
class MPS_Handler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip().decode()
        socket = self.request[1]

        data = data.split()
        data_type = data[0]
        parameters = data[1:]

        if data_type == "telemetry":
            # Receive location data
            current_lat = str(parameters[0]).strip(' b\'')
            current_lng = str(parameters[1]).strip(' b\'')
            current_alt = str(parameters[2]).strip(' b\'')
            current_rol = str(parameters[3]).strip(' b\'')
            current_pch = str(parameters[4]).strip(' b\'')
            current_yaw = str(parameters[5]).strip(' b\'')
            current_asp = str(parameters[6]).strip(' b\'')
            current_gsp = str(parameters[7]).strip(' b\'')
            current_btv = str(parameters[8]).strip(' b\'')
            current_wpn = str(parameters[9]).strip(' b\'')
            wind_dir = str(parameters[10]).strip(' b\'')
            wind_vel = str(parameters[11]).strip(' b\'')

            #print(f"Current Location: lat: {current_lat} lng: {current_lng} alt: {current_alt}")
            #print(f"                  hdg: {current_hdg} vel: {current_vel}")

            # Updated shared obj with location data
            self.server._so.mps_status_set({"airspeed":float(current_asp), "groundspeed":float(current_gsp), "latitude":float(current_lat), "longitude":float(current_lng), "altitude":float(current_alt), "heading":float(current_yaw), "batteryvoltage":float(current_btv), "winddirection":float(wind_dir), "windvelocity":float(wind_vel)})

            # Send instruction to UAV
            socket.sendto(bytes(self.next_instruction(int(float(current_wpn))), "utf-8"), self.client_address)
        
        elif data_type == "queue":
            #receive data about current queue
            wp_count = int(parameters[0])
            wp_list = []

            for i in range(0, wp_count):
                wp_list.append(Waypoint("","", float(parameters[1 + 3*i]), float(parameters[1 + 3*i + 1]), float(parameters[1 + 3*i + 2])))
            
            print(f"DEBUG Recieved Waypoint List ({wp_count}):")
            for i in range(0, wp_count):
                print(f"{wp_list[i]._lat} {wp_list[i]._lng} {wp_list[i]._alt}")
            self.server._so.mps_currentmission_updatequeue(wp_list)
    
    def next_instruction(self, current_wpn):
        # Place new instructions onto the queue
        instruction = ""

        # Check if we should send back updated mission queue
        if self.server._so.mps_currentmission_shouldupdate():
            self.server._instructions.push(f"QGET")

        # Check if there is a flight config update request
        newmode = self.server._so.flightConfig_get()
        if newmode != "":
            self.server._instructions.push(f"CONFIG {newmode}")
        
        altitude_standard = self.server._so.altitude_standard_get()
        if altitude_standard != "":
            self.server._instructions.push(f"ALTSTD {altitude_standard}")

        # Check if there is a new home
        newhome = self.server._so.mps_newhome_get()
        if newhome != None:
            wp = Waypoint(newhome['id'], newhome['name'], newhome['latitude'], newhome['longitude'], newhome['altitude'])
            self.server._instructions.push(f"HOME {str(wp)}")

        vtol_land = self.server._so.mps_vtol_land_get()
        if vtol_land != None:
            wp = Waypoint(vtol_land['id'], vtol_land['name'], vtol_land['latitude'], vtol_land['longitude'], vtol_land['altitude'])
            self.server._instructions.push(f"VTOLLAND {str(wp)}")

        # Check takeoff altitude
        takeoffalt = self.server._so.mps_takeoffalt_get()
        if takeoffalt != 0:
            self.server._instructions.push(f"TOFF {takeoffalt}")

        # Check if we should rtl
        elif self.server._so._rtl_flag:
            self.server._instructions.push(f"RTL {self.server._so.mps_rtl_get()}")
        
        # Check if we should land
        elif self.server._so.mps_landing_get():
            self.server._instructions.push("LAND")
        
        # Check if we should change flight mode
        elif self.server._so.mps_vtol_get() != self.server._flight_mode:
            self.server._flight_mode = self.server._so.mps_vtol_get()
            self.server._instructions.push(f"MODE {self.server._flight_mode}")
        
        # Check if we should send tts text
        elif self.server._so._voice_flag:
            text = self.server._so.voice_get()
            self.server._instructions.push(f"TTS {text}")

        # Check if we should switch modes
        elif self.server._so._flightmode_flag:
            mode = self.server._so.flightmode_get()
            self.server._instructions.push(f"FMDE {mode}")

        # Check if we should lock
        elif self.server._so.mps_locked_get():
            print("Locking...")
            if self.server._locked:
                # Still locked, idle
                #self.server._instructions.push("IDLE")
                pass
            else:
                # Send the lock instruction
                self.server._instructions.push("LOCK 1")
                self.server._locked = True
        else:
            # reset _locked if coming out of locked state
            if self.server._locked:
                self.server._instructions.push("LOCK 0")
                self.server._locked = False
            
            # Check for a new waypoint to push
            push_wp = self.server._so.append_wp_get()
            if push_wp:
                self.server._instructions.push(f"PUSH {str(push_wp)}")

            # Check for a new mission
            nextwpq = self.server._so.mps_newmission_get()
            if nextwpq != None:
                # Overwrite the current mission with the new one
                print("New mission found!")
                self.server._current_mission = Mission(nextwpq)
                
                # Place instructions for the new mission onto the queue
                self.server._instructions.push("NEWM")
                self.server._newmc = 1
                while (not nextwpq.empty()):
                    curr = nextwpq.pop()
                    self.server._instructions.push(f"NEXT {str(curr)}")
                    self.server._newmc += 1
                self.server._instructions.push("NEXT")
            else:
                # Keep going and send current wpno to shared obj
                if (self.server._newmc == 0):
                    self.server._so.mps_currentmission_update(current_wpn)
                else:
                    self.server._newmc -= 1
                #self.server._instructions.push("CONT")
                pass

        # Retrieve an instruction
        if (self.server._instructions.empty()):
            return "IDLE"
        else:
            instruction = self.server._instructions.pop()
            print("instruction", instruction)
            return instruction
            

class MPS_Internal_Server(socketserver.UDPServer):
    def __init__(self, hptuple, handler, so):
        self._so = so

        self._current_mission = Mission() # Empty mission
        self._instructions = Queue()

        self._locked = False
        self._newmc = 0
        self._flight_mode = 3

        # Superclass constructor
        super().__init__(hptuple, handler)
        print("MPS_Internal_Server initialized")

class MPS_Server():
    def __init__(self, so):
        self._so = so

        print("MPS_Server initialized")

    def serve_forever(self):
        HOST, PORT = "localhost", 9001
        self._server = MPS_Internal_Server((HOST, PORT), MPS_Handler, self._so)
        self._server.serve_forever()

if __name__ == "__main__":
    testobj = SharedObject()

    server = MPS_Server(testobj)
    server.serve_forever()
