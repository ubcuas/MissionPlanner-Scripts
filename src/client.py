#Python 2.7

import socket
import sys
import math
import clr
import time
import re, string
clr.AddReference("MissionPlanner.Utilities")
import MissionPlanner #import *
clr.AddReference("MissionPlanner.Utilities") #includes the Utilities class
from MissionPlanner.Utilities import Locationwp

HOST = 'localhost'   # Symbolic name meaning all available interfaces
#SPORT = 5000 # Arbitrary non-privileged port  
RPORT = 4000 # Arbitrary non-privileged port

REMOTE = ''
# Datagram (udp) socket 

rsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
print("Sockets Created")

Script.ChangeMode("Guided") # changes mode to "Guided"
print("Entered Guided Mode")

#keep talking with the Mission Planner server 
while 1: 
    print("Loop begin")
    #send location to server
    location = "{:} {:} {:} {:} {:}".format(cs.lat, cs.lng, cs.alt, cs.yaw, cs.airspeed)
    rsock.sendto(location, (HOST, RPORT))

    #recieve waypoint from server
    msg = rsock.recv(1024)
    parameters = msg.split()

    state = parameters[0]
    arg1 = parameters[1]
    arg2 = parameters[2]
    arg3 = parameters[3]
    
    if cs.mode == 'MANUAL': #Safety Manual Mode Switch
        Script.ChangeMode("Manual")
        break
    else:
        if state == "NEXT":
            float_lat = float(arg1)
            float_lng = float(arg2)
            float_alt = float(arg3)

            #waypoint creation
            item = MissionPlanner.Utilities.Locationwp() # creating waypoint
            MissionPlanner.Utilities.Locationwp.lat.SetValue(item,float_lat)
            MissionPlanner.Utilities.Locationwp.lng.SetValue(item,float_lng)
            MissionPlanner.Utilities.Locationwp.alt.SetValue(item,float_alt)
            MAV.setGuidedModeWP(item) #set waypoint

            print("Waypoint set at lat: {:} lng: {:} alt: {:}".format(float_lat, float_lng, float_alt))
        
        elif state == "IDLE":
            pass #do nothing

        elif state == "LOCK":
            #extremely scuffed - set UAV to LOITER, then immediately switch back to GUIDED
            #change once we find a better way to remove a guided mode wp
            Script.ChangeMode("Loiter")
            Script.ChangeMode("Guided")

        else:
            print("unrecognized commmand {:}".format(state))

    #timing
    time.sleep(1)

# exit
rsock.close()
print("Script End")
