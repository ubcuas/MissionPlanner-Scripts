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
    location = "{:} {:} {:} {:} {:} {:} {:}".format(cs.lat, cs.lng, cs.alt, cs.yaw, cs.airspeed, cs.battery_voltage, cs.wpno)
    rsock.sendto(location, (HOST, RPORT))

    #print("Waypoint Count", MAV.getWPCount())

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

            Script.ChangeMode("Guided")
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
                MAV.setWPTotal(len(wp_array) + 1)
                #upload waypoints
                dummy = Locationwp()
                Locationwp.lat.SetValue(dummy, 0)
                Locationwp.lng.SetValue(dummy, 0)
                Locationwp.alt.SetValue(dummy, 0)
                Locationwp.id.SetValue(dummy, int(MAVLink.MAV_CMD.WAYPOINT))
                MAV.setWP(dummy, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
                for i in range(0, len(wp_array)):
                    wp = Locationwp()
                    Locationwp.lat.SetValue(wp, wp_array[i][0])
                    Locationwp.lng.SetValue(wp, wp_array[i][1])
                    Locationwp.alt.SetValue(wp, wp_array[i][2])
                    Locationwp.id.SetValue(wp, int(MAVLink.MAV_CMD.WAYPOINT))
                    MAV.setWP(wp, i + 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
                #final ack
                MAV.setWPACK()
                #empty array
                wp_array = []
                #enter auto mode
                Script.ChangeMode("Auto")
                print("NEXT - new mission set")

        elif cmd == "CONT":
            #CONT - continue
            #print("CONT")
            pass
        elif cmd == "IDLE":
            #IDLE - do nothing
            #print("IDLE")
            pass
        elif cmd == "LOCK":
            #LOCK - lock/unlock the UAV
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
                #set up takeoff waypoint
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
                MAV.setWP(home,0,MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
                MAV.setWP(takeoff,1,MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
                MAV.setWPACK()
                Script.ChangeMode("Guided")
                print("YOU HAVE 5 SECONDS TO ARM MOTORS")
                time.sleep(5)
                Script.ChangeMode("Auto")
                MAV.doCommand(MAVLink.MAV_CMD.MISSION_START,0,0,0,0,0,0,0) #arm motors
                print("TOFF - takeoff to {:}m".format(takeoffalt))
            else:
                print("TOFF - invalid command", msg)

        elif cmd == "HOME":
            home = Locationwp()
            Locationwp.id.SetValue(home, int(MAVLink.MAV_CMD.WAYPOINT))
            Locationwp.lat.SetValue(home, float(argv[0]))
            Locationwp.lng.SetValue(home, float(argv[1]))
            Locationwp.alt.SetValue(home, 0)
            MAV.setWP(home, 0, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)

        elif cmd == "RTL":
            # rtl = Locationwp()
            # Locationwp.id.SetValue(rtl, int(MAVLink.MAV_CMD.RETURN_TO_LAUNCH))
            # MAV.setWP(rtl, 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
            # MAV.setWPTotal(2)
            # MAV.setWPACK()
            MAV.doCommand(MAVLink.MAV_CMD.RETURN_TO_LAUNCH,0,0,0,0,0,0,0)
            print("RTL - returning to launch")

        elif cmd == "LAND":
            # land = Locationwp()
            # Locationwp.id.SetValue(land, int(MAVLink.MAV_CMD.LAND))
            # Locationwp.lat.SetValue(land, cs.lat)
            # Locationwp.lng.SetValue(land, cs.lng)
            # Locationwp.alt.SetValue(land, 0)
            # MAV.setWP(land, 1, MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT)
            # MAV.setWPTotal(2)
            # MAV.setWPACK()
            MAV.doCommand(MAVLink.MAV_CMD.LAND,0,0,0,0,cs.lat,cs.lng,cs.alt)
            print("LAND - landing in place")
        
        else:
            print("unrecognized command", cmd, argv)

    #timing
    time.sleep(1)

# exit
rsock.close()
print("Script End")
