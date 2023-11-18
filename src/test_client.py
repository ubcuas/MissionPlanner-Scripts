import socket
import time
import logging


'''
Test Client for simulating MissionPlanner, used for testing MPS
'''

HOST = 'localhost'   # Symbolic name meaning all available interfaces
#SPORT = 5000 # Arbitrary non-privileged port  
RPORT = 4000 # Arbitrary non-privileged port
DELAY = 10
MAV = {}


MAVLink = {
    "MAV_CMD": {
        "WAYPOINT": 1,
        "TAKEOFF": 5
    },

    "MAV_FRAME": {
        "GLOBAL": 10
    }
}

rsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
print("Sockets Created")


### Simulated Object Classes
class MissionPlannerSimulatedObj:

    # dummy values for constructor
    def __init__(self):
        self.lat = 38.3151389
        self.lng = -75.5487511
        self.pitch = 0
        self.alt = 0
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.airspeed = 0
        self.groundspeed = 0
        self.battery_voltage = 12
        self.wpno = 0
        self.mode = "AUTO"

# Simulated object of MissionPlanner data
cs = MissionPlannerSimulatedObj()

class ScriptSimulatedObj:

    def __init__(self, mps_sim):
        self.mps_sim = mps_sim
    
    def ChangeMode(self, mode):
        self.mps_sim.mode = mode

Script = ScriptSimulatedObj(cs)

def upload_mission(wp_array):
    """
    Uploads a mission to the aircraft based on a given set of waypoints.

    Parameters:
        - wp_array: ordered list of waypoints
    """
    # Set waypoint total

    # SIMULATED VERSION NEEDS TO BE UPLOADED

class ValueContainerInt:

    def __init__(self, val):
        self.val = val
    
    def SetValue(lwp, new_val):
        self.val = new_val

class Locationwp:
    id = ValueContainerInt(0)
    lat = ValueContainerInt(0)
    lng = ValueContainerInt(0)
    alt = ValueContainerInt(0)

    def __init__(self):
        self.id = ValueContainerInt(0)
        self.lat = ValueContainerInt(0)
        self.lng = ValueContainerInt(0)
        self.alt = ValueContainerInt(0)


while True:
    
    location = "{:} {:} {:} {:} {:} {:} {:}".format(cs.lat, cs.lng, cs.alt, cs.yaw, cs.airspeed, cs.battery_voltage, cs.wpno)
    location = location.encode("utf-8")
    rsock.sendto(location, (HOST, RPORT))

    msg = rsock.recv(1024).decode('utf-8')

    wp_array = []
    
    # cmd = msg.split().split()[0]

    # if (msg != "IDLE"):
    #     print(f"{counter}: {msg}")

    argv = msg.split()
    cmd = argv.pop(0)
    
    if cs.mode == 'MANUAL': # Safety Manual Mode Switch
        Script.ChangeMode("Manual")
        print("Entered Manual Mode")
        break
    else:
        if cmd == "NEWM":
            # NEWM - newmission
            # Enter stabilize and await new mission waypoints

            Script.ChangeMode("Guided")
            wp_array = []
            print("NEWM")

        elif cmd == "NEXT":
            # NEXT - next waypoint
            # Receive another waypoint, or start the mission if no more waypoints

            if (len(argv) > 0):
                # Receive waypoint
                if (len(argv) != 3):
                    print("NEXT - invalid waypoint {:}".format(msg))
                else:
                    float_lat = float(argv[0])
                    float_lng = float(argv[1])
                    float_alt = float(argv[2])

                    wp_array.append((float_lat, float_lng, float_alt))
                    print("NEXT - received waypoint {:} {:} {:}".format(float_lat, float_lng, float_alt))

                    if (len(wp_array) == 1):
                        #set immediate mission - aircraft reacts immediately to first waypoint
                        upload_mission(wp_array)
                        # Enter auto mode
                        Script.ChangeMode("Auto")
                        print("NEXT - moving to first waypoint")

            else: 
                upload_mission(wp_array)
                # Empty array
                wp_array = []
                # Enter auto mode
                Script.ChangeMode("Auto")
                print("NEXT - new mission set")

        elif cmd == "CONT":
            # CONT - continue
            #print("CONT")
            pass
        elif cmd == "IDLE":
            # IDLE - do nothing
            #print("IDLE")
            pass
        elif cmd == "LOCK":
            # LOCK - lock/unlock the UAV
            flag = int(argv[0])
            if flag:
                #lock the UAV
                Script.ChangeMode("Guided")
                print("LOCK - locked the UAV")
            else:
                #unlock the UAV
                Script.ChangeMode("Auto")
                print("LOCK - unlocked the UAV")

        elif cmd == "TOFF":
            if (len(argv) == 1):
                takeoffalt = float(argv[0])
                Script.ChangeMode("Loiter")
                # Set up takeoff waypoint
                home = Locationwp()
                Locationwp.id.SetValue(home, int(MAVLink[MAV_CMD][WAYPOINT]))
                Locationwp.lat.SetValue(home, cs.lat)
                Locationwp.lng.SetValue(home, cs.lng)
                Locationwp.alt.SetValue(home, 0)
                takeoff = Locationwp()
                Locationwp.id.SetValue(takeoff, int(MAVLink[MAV_CMD][TAKEOFF]))
                Locationwp.lat.SetValue(takeoff, cs.lat)
                Locationwp.lng.SetValue(takeoff, cs.lng)
                Locationwp.alt.SetValue(takeoff, takeoffalt)

                MAV.setWPTotal(2)
                MAV.setWP(home,0,MAVLink.MAV_FRAME.GLOBAL)
                MAV.setWP(takeoff,1,MAVLink.MAV_FRAME.GLOBAL)
                MAV.setWPACK()
                Script.ChangeMode("Guided")
                print("YOU HAVE 10 SECONDS TO ARM MOTORS")
                time.sleep(10)
                Script.ChangeMode("Auto")
                MAV.doCommand(MAVLink.MAV_CMD.MISSION_START,0,0,0,0,0,0,0) # Arm motors
                print("TOFF - takeoff to {:}m".format(takeoffalt))
            else:
                print("TOFF - invalid command", msg)

        elif cmd == "HOME":
            MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME,0,0,0,0,float(argv[0]),float(argv[1]),float(argv[2]))
            print("HOME - set a new home")

        elif cmd == "RTL":
            MAV.doCommand(MAVLink.MAV_CMD.RETURN_TO_LAUNCH,0,0,0,0,0,0,0)
            print("RTL - returning to launch")

        elif cmd == "LAND":
            MAV.doCommand(MAVLink.MAV_CMD.LAND,0,0,0,0,cs.lat,cs.lng,0)
            print("LAND - landing in place")
        
        elif cmd == "VTOLLAND":
            landlat = float(argv[0])
            landlng = float(argv[1])

            # Set up landing waypoint
            home = Locationwp()
            Locationwp.id.SetValue(home, int(MAVLink.MAV_CMD.WAYPOINT))
            Locationwp.lat.SetValue(home, landlat)
            Locationwp.lng.SetValue(home, landlng)
            Locationwp.alt.SetValue(home, 0)
            landing = Locationwp()
            Locationwp.id.SetValue(landing, int(MAVLink.MAV_CMD.VTOL_LAND))
            Locationwp.lat.SetValue(landing, landlat)
            Locationwp.lng.SetValue(landing, landlng)
            Locationwp.alt.SetValue(landing, takeoffalt)

            MAV.setWPTotal(2)
            MAV.setWP(home,0,MAVLink.MAV_FRAME.GLOBAL)
            MAV.setWP(landing,1,MAVLink.MAV_FRAME.GLOBAL)
            MAV.setWPACK()
            Script.ChangeMode("Auto")
            # MAV.doCommand(MAVLink.MAV_CMD.LAND,0,0,0,0,cs.lat,cs.lng,0)
            print("LAND - landing at {:}, {:}".format(landlat, landlng))
        
        elif cmd == "MODE":
            MAV.doCommand(MAVLink.MAV_CMD.DO_VTOL_TRANSITION,int(argv[0]),0,0,0,0,0,0)
        
        elif cmd == "FMDE":
            if MODE == 'plane' and argv[0] in ['loiter', 'stabilize']:
                Script.ChangeMode("q{:}".format(argv[0]))
            else:
                Script.ChangeMode(argv[0])
        
        elif cmd == "TTS":
            text = ""
            for word in argv:
                text += word + " "
            fprint("TTS: ", text)
        
        elif cmd == "CONFIG":
            if argv[0] in ["vtol", "plane"]:
                MODE = argv[0]
                print(MODE)

        else:
            print("unrecognized command", cmd, argv)

        #timing
    time.sleep(DELAY)