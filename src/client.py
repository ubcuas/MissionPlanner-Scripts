#Python 2.7

import socket
import time
import clr
clr.AddReference("MissionPlanner.Utilities")
import MissionPlanner #import *
clr.AddReference("MissionPlanner.Utilities") #includes the Utilities class
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink")
import MAVLink

HOST = 'localhost'   # Symbolic name meaning all available interfaces
#SPORT = 5000 # Arbitrary non-privileged port  
RPORT = 4000 # Arbitrary non-privileged port

REMOTE = ''
# Datagram (udp) socket 

rsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
print("Sockets Created")

Script.ChangeMode("Guided") # changes mode to "Guided"
print("Entered Guided Mode")

wp_array = []

#keep talking with the Mission Planner server 
while 1: 
    print("Loop begin")
    #send location to server
    location = "{:} {:} {:} {:} {:}".format(cs.lat, cs.lng, cs.alt, cs.yaw, cs.airspeed)
    rsock.sendto(location, (HOST, RPORT))

    print("Waypoint Count", MAV.getWPCount())

    #recieve waypoint from server
    msg = rsock.recv(1024)

    argv = msg.split()
    cmd = argv.pop(0)
    
    if cs.mode == 'MANUAL': #Safety Manual Mode Switch
        Script.ChangeMode("Manual")
        break
    else:
        if cmd == "NEWM":
            #NEWM - newmission
            #enter stabilize and await new mission waypoints

            Script.ChangeMode("Stabilize")
            wp_array = []
            print("NEWM")

        elif cmd == "NEXT":
            #NEXT - next waypoint
            #receive another waypoint, or start the mission if no more waypoints

            if (len(argv) > 0):
                #recieve waypoint
                if (len(argv) != 3):
                    print("NEXT - invalid waypoint {:}".format(msg))
                else:
                    float_lat = float(argv[0])
                    float_lng = float(argv[1])
                    float_alt = float(argv[2])

                    wp_array.append((float_lat, float_lng, float_alt))
                    print("NEXT - received waypoint {:} {:} {:}".format(float_lat, float_lng, float_alt))
            else: 
                #set waypoint total
                MAV.setWPTotal(len(wp_array))
                #upload waypoints
                for i in range(0, len(wp_array)):
                    wp = Locationwp()
                    Locationwp.lat.SetValue(wp, wp_array[i][0])
                    Locationwp.lng.SetValue(wp, wp_array[i][1])
                    Locationwp.alt.SetValue(wp, wp_array[i][2])
                    Locationwp.id.SetValue(wp, int(MAVLink.MAV_CMD.WAYPOINT))
                    MAV.setWP(wp, i, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
                #final ack
                MAV.setWPACK()
                #empty array
                wp_array = []
                #enter auto mode
                Script.ChangeMode("Auto")
                print("NEXT - new mission set")

        elif cmd == "CONT":
            #CONT - continue
            print("CONT")

        elif cmd == "IDLE":
            #IDLE - do nothing
            print("IDLE")

        elif cmd == "LOCK":
            #LOCK - lock/unlock the UAV
            flag = int(argv[0])
            if flag:
                #lock the UAV
                Script.ChangeMode("Stabilize")
                print("LOCK - locked the UAV")
            else:
                #unlock the UAV
                Script.ChangeMode("Auto")
                print("LOCK - unlocked the UAV")

        elif cmd == "TOFF":
            if (len(argv) == 1):
                takeoffalt = float(argv[0])
                Script.ChangeMode("Loiter")
                #set up takeoff waypoint
                home = Locationwp()
                Locationwp.id.SetValue(home, int(MAVLink.MAV_CMD.TAKEOFF))
            else:
                print("TOFF - invalid command", msg)

        else:
            print("unrecognized command", cmd, argv)

    #timing
    time.sleep(1)

# exit
rsock.close()
print("Script End")
