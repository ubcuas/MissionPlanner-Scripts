import socketserver
import struct

from server.common.missions import Mission
from server.common.wpqueue import Waypoint, Queue
from server.common.sharedobject import SharedObject
from server.common.encoders import waypoint_encode, waypoint_decode, waypoint_size
from server.common.status import Status

# Define request handler
class MPS_Handler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        """
        Handles one 'cycle' of MPS <-> client communications.
        Performs different actions based on the recieved datatype:
            telemetry:  This is the main 'back and forth' between the client and MPS.
                        Here, we receive an update from the client with the latest drone telemetry.
                        In turn, MPS responds with the next instruction indicating what the drone
                        should do this cycle.

            queue:      This is data about the current queue as it is in MissionPlanner. 

            success_takeoff, success_arm: Indicates whether a takeoff or arm command was successful. 
        """

        self.server: MPS_Internal_Server

        rawdata = self.request[0]
        socket = self.request[1]

        data = rawdata.strip()

        #the first two bytes are for the header
        data_type = data[0:2]
        payload = data[2:]

        if data_type == b"TL": #telemetry
            status = Status()
            status.decode_status(payload)

            # Updated shared obj with location data
            self.server._so.set_status(status)

            # Send instruction to UAV
            socket.sendto(self.next_instruction(int(float(status._wpn))), self.client_address)
        
        elif data_type == b"QI": #queue info, receive data about current queue
            #unpack the number of waypoints from the first byte
            wp_count = payload[0]
            wp_list: list[Waypoint] = []
            idx = 1

            for i in range(0, wp_count):
                wp_list.append(waypoint_decode(payload[idx : idx + waypoint_size()]))
                idx += waypoint_size()
            
                #TODO - ID resolution would occur here

            print(f"DEBUG Recieved Waypoint List ({wp_count}):")
            for i in range(0, wp_count):
                print(f"{wp_list[i].get_coords_gps()} {wp_list[i].get_command()}")

            self.server._so.mps_currentmission_updatequeue(wp_list)
        
        elif data_type == b"ST": #successful takeoff
            #first byte of payload is indicator
            result = payload[0]
            if result == 1:
                #successful takeoff
                print("Successful takeoff")
            else:
                #unsuccessful
                print("Unsuccessful takeoff")
            self.server._so.takeoff_set_result(result)

        elif data_type == b"SA": #successful arm
            #first byte of payload is indicator
            result = payload[0]
            if result == 1:
                print("Successful arm/disarm")
            else:
                print("Unsuccessful arm/disarm")
            self.server._so.arm_set_result(result)
    
    def next_instruction(self, current_wpn):
        """Returns the next instruction to be sent to the drone."""
        
        self.check_shared_object(current_wpn)

        # Retrieve an instruction
        if (self.server._instructions.empty()):
            return b"IDLE"
        else:
            instruction = self.server._instructions.pop()
            if (type(instruction) != bytes):
                print("instruction", instruction)
                return bytes(instruction, "utf-8")
            else:
                print(f"packed bytes: length {len(instruction)}",)
            return instruction
    
    def check_shared_object(self, current_wpn):
        """Check shared object for new directives, and place instructions on the queue if necessary."""

        instruction = ""

        # Check if we should send back updated mission queue
        if self.server._so.mps_currentmission_shouldupdate():
            self.server._instructions.push(f"QUEUE_GET")

        # Check if there is a flight config update request
        newmode = self.server._so.flightConfig_get()
        if newmode != "":
            self.server._instructions.push(f"CONFIG {newmode}")
        
        # Check if we should change our altitude standard
        altitude_standard = self.server._so.altitude_standard_get()
        if altitude_standard != "":
            self.server._instructions.push(f"ALTSTD {altitude_standard}")

        # Check if there is a new home
        newhome = self.server._so.mps_newhome_get()
        if newhome != None:
            wp = Waypoint(newhome['id'], newhome['name'], newhome['latitude'], newhome['longitude'], newhome['altitude'])
            self.server._instructions.push(f"HOME {str(wp)}")

        # Check if we need to land
        land_at_pos = self.server._so.land_at_pos_get()
        if land_at_pos != None:
            wp = Waypoint(land_at_pos['id'], land_at_pos['name'], land_at_pos['latitude'], land_at_pos['longitude'], land_at_pos['altitude'])
            self.server._instructions.push(f"LAND_AT_POS {str(wp)}")

        # Check takeoff altitude
        takeoffalt = self.server._so.mps_takeoffalt_get()
        if takeoffalt != 0:
            self.server._instructions.push(f"TAKEOFF {takeoffalt}")

        # Check if we should rtl
        elif self.server._so._rtl_flag:
            self.server._instructions.push(f"RTL {self.server._so.mps_rtl_get()}")
        
        # Check if we should land
        elif self.server._so.mps_landing_get():
            self.server._instructions.push("LAND")

        # Check if we should switch modes
        elif self.server._so._flightmode_flag:
            mode = self.server._so.flightmode_get()
            self.server._instructions.push(f"FLIGHT_MODE {mode}")
        
        # Check if we should arm/disarm the motors
        arm = self.server._so.arm_get()
        if arm is not None:
            print("ARMING...")
            self.server._instructions.push(f"ARM {arm}")
            
        # Check for a new waypoint to push
        push_wp = self.server._so.append_wp_get()
        if push_wp:
            self.server._instructions.push(f"PUSH {str(push_wp)}")

        # Check for a new insertion
        insertwpq = self.server._so.mps_newinsert_get()
        if insertwpq != None:
            # Place instruction for new insertion onto the queue
            self.server._instructions.push(f"NEW_INSERT {0}")

            # Prepare packed mission
            missionbytes = b""
            while (not insertwpq.empty()):
                curr: Waypoint = insertwpq.pop()
                missionbytes += waypoint_encode(curr)
            self.server._instructions.push(missionbytes)

        # Check for a new mission
        nextwpq = self.server._so.mps_newmission_get()
        if nextwpq != None:
            # Overwrite the current mission with the new one
            print("New mission found!")
            self.server._current_mission = Mission(nextwpq)
            
            # Place instruction for the new mission onto the queue
            self.server._instructions.push("NEW_MISSION")

            #Prepare packed mission
            missionbytes = b""

            self.server._newmc = 1
            while (not nextwpq.empty()):
                curr: Waypoint = nextwpq.pop()
                self.server._newmc += 1
                missionbytes += waypoint_encode(curr)

            self.server._instructions.push(missionbytes)
        else:
            # Keep going and send current wpno to shared obj
            if (self.server._newmc == 0):
                self.server._so.mps_currentmission_update(current_wpn)
            else:
                self.server._newmc -= 1
            #self.server._instructions.push("CONT")
            pass

class MPS_Internal_Server(socketserver.UDPServer):
    def __init__(self, hptuple, handler, so: SharedObject):
        self._so: SharedObject = so

        self._current_mission = Mission() # Empty mission
        self._instructions = Queue()

        self._newmc: int = 0

        # Superclass constructor
        super().__init__(hptuple, handler)
        #print("MPS_Internal_Server initialized")

class MPS_Server():
    def __init__(self, so: SharedObject):
        self._so: SharedObject = so

        #print("MPS_Server initialized")

    def serve_forever(self):
        print("MissionPlanner Server starting...")
        HOST, PORT = "localhost", 9001
        self._server = MPS_Internal_Server((HOST, PORT), MPS_Handler, self._so)
        self._server.serve_forever()

if __name__ == "__main__":
    testobj = SharedObject()

    server = MPS_Server(testobj)
    server.serve_forever()
