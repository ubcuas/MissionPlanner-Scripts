#Python 2.7

import socket
import time
import clr
clr.AddReference("MissionPlanner.Utilities")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities") # Includes the Utilities class
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink")
import MAVLink

MissionPlanner.MainV2.speechEnable = True

HOST = 'localhost' # Symbolic name meaning all available interfaces
#SPORT = 5000 # Arbitrary non-privileged port  
RPORT = 4000 # Arbitrary non-privileged port

DELAY = 1 # Seconds

REMOTE = ''
# Datagram (udp) socket 

rsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
timeout = 5
rsock.settimeout(timeout)
print("Sockets Created")

Script.ChangeMode("Guided") # Changes mode to "Guided"
print("Entered Guided Mode")

wp_array = []
fence_exclusive = False
fence_type = ""

def upload_mission(wp_array):
    """
    Uploads a mission to the aircraft based on a given set of waypoints.

    Parameters:
        - wp_array: ordered list of waypoints
    """
    # Set waypoint total
    MAV.setWPTotal(len(wp_array) + 1)
    # Upload waypoints
    dummy = Locationwp()
    Locationwp.lat.SetValue(dummy, 0)
    Locationwp.lng.SetValue(dummy, 0)
    Locationwp.alt.SetValue(dummy, 0)
    Locationwp.id.SetValue(dummy, int(MAVLink.MAV_CMD.WAYPOINT))
    MAV.setWP(dummy, 0, MAVLink.MAV_FRAME.GLOBAL)
    for i in range(0, len(wp_array)):
        wp = Locationwp()
        Locationwp.lat.SetValue(wp, wp_array[i][0])
        Locationwp.lng.SetValue(wp, wp_array[i][1])
        Locationwp.alt.SetValue(wp, wp_array[i][2])
        Locationwp.id.SetValue(wp, int(MAVLink.MAV_CMD.WAYPOINT))
        MAV.setWP(wp, i + 1, MAVLink.MAV_FRAME.GLOBAL)
    # Final ack
    MAV.setWPACK()

MissionPlanner.MainV2.speechEngine.SpeakAsync("Ready to receive requests")

# Keep talking with the Mission Planner server 
while 1:
    # Send location to server
    location = "{:} {:} {:} {:} {:} {:} {:}".format(cs.lat, cs.lng, cs.alt, cs.yaw, cs.airspeed, cs.battery_voltage, cs.wpno)
    rsock.sendto(location, (HOST, RPORT))

    #print("Waypoint Count", MAV.getWPCount())

    try:
        msg = rsock.recv(1024)
    except socket.timeout:
        print("Socket timeout")
        time.sleep(DELAY)
        continue
    except socket.error:
        print("Socket error - trying again in 10 seconds...")
        MissionPlanner.MainV2.speechEngine.SpeakAsync("Socket connection error. Trying again in 10 seconds.")
        time.sleep(10)
        continue

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
                Locationwp.id.SetValue(home, int(MAVLink.MAV_CMD.WAYPOINT))
                Locationwp.lat.SetValue(home, cs.lat)
                Locationwp.lng.SetValue(home, cs.lng)
                Locationwp.alt.SetValue(home, 0)
                takeoff = Locationwp()
                Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.TAKEOFF))
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
            # Set up landing waypoint
            home = Locationwp()
            Locationwp.id.SetValue(home, int(MAVLink.MAV_CMD.WAYPOINT))
            Locationwp.lat.SetValue(home, cs.lat)
            Locationwp.lng.SetValue(home, cs.lng)
            Locationwp.alt.SetValue(home, 0)
            landing = Locationwp()
            Locationwp.id.SetValue(landing, int(MAVLink.MAV_CMD.LAND))
            Locationwp.lat.SetValue(landing, cs.lat)
            Locationwp.lng.SetValue(landing, cs.lng)
            Locationwp.alt.SetValue(landing, takeoffalt)

            MAV.setWPTotal(2)
            MAV.setWP(home,0,MAVLink.MAV_FRAME.GLOBAL)
            MAV.setWP(landing,1,MAVLink.MAV_FRAME.GLOBAL)
            MAV.setWPACK()
            Script.ChangeMode("Auto")
            # MAV.doCommand(MAVLink.MAV_CMD.LAND,0,0,0,0,cs.lat,cs.lng,0)
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
        
        elif cmd == "NEWF":
            Script.ChangeMode('Guided')
            if argv[0] == "EXCLUSIVE":
                fence_exclusive = True
            elif argv[0] == "INCLUSIVE":
                fence_exclusive = False
            else:
                Script.ChangeMode('Auto')
                print("NEWF - unrecognized argument, should be INCLUSIVE or EXCLUSIVE")

            fence_type = argv[1]
            if (fence_type != "POLYGON" and fence_type != "CIRCLE"):
                Script.ChangeMode('Auto')
                print("NEWF - unrecognized argument, should be POLYGON or CIRCLE")
        
        elif cmd == "FENCE":
            # FENCE - next fencepost
            # Receive another fencepost, or set the fence if no more fenceposts

            if fence_type == "POLYGON":
                if (len(argv) > 0):
                    # Receive fencepost
                    if (len(argv) != 3):
                        print("FENCE - invalid fencepost {:}".format(msg))
                    else:
                        float_lat = float(argv[0])
                        float_lng = float(argv[1])
                        float_alt = float(argv[2])

                        wp_array.append((float_lat, float_lng, float_alt))
                        print("FENCE - received fencepost {:} {:} {:}".format(float_lat, float_lng, float_alt))
                else: 
                    # Upload fenceposts
                    for fp in wp_array:
                        if (fence_exclusive):
                            MAV.doCommand(MAVLink.MAV_CMD.FENCE_POLYGON_VERTEX_EXCLUSION,len(wp_array),0,0,0,fp[0],fp[1],0)
                        else:
                            MAV.doCommand(MAVLink.MAV_CMD.FENCE_POLYGON_VERTEX_INCLUSION,len(wp_array),0,0,0,fp[0],fp[1],0)

                    # Empty array
                    wp_array = []
                    # Enter auto mode
                    Script.ChangeMode("Auto")
                    print("FENCE - new fence set")
                    fence_type = ""
            else:
                # CIRCLE fences are specified by a single FENCE instruction
                if (len(argv) != 4):
                    print("FENCE - invalid fencepost {:}".format(msg))
                else:
                    float_lat = float(argv[0])
                    float_lng = float(argv[1])
                    float_alt = float(argv[2])
                    float_rad = float(argv[3])

                    if (fence_exclusive):
                        MAV.doCommand(MAVLink.MAV_CMD.FENCE_CIRCLE_EXCLUSION,float_rad,1,0,0,float_lat,float_lng,0)
                    else:
                        MAV.doCommand(MAVLink.MAV_CMD.FENCE_CIRCLE_INCLUSION,float_rad,1,0,0,float_lat,float_lng,0)
                    
                    MAV.doCommand(MAVLink.MAV_CMD.DO_FENCE_ENABLE,1,0,0,0,0,0,0)

                    print("FENCE - set circular fence with center {:} {:}, radius {:}".format(float_lat, float_lng, float_rad))

        else:
            print("unrecognized command", cmd, argv)

    #timing
    time.sleep(DELAY)

# exit
rsock.close()
print("Script End")