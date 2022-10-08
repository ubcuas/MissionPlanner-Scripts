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
    #send location to server
    location = "{:} {:} {:}".format(cs.lat, cs.lng, cs.alt)
    rsock.sendto(location, (HOST, RPORT))

    #recieve waypoint from server
    msg = rsock.recv(1024)
    parameters = msg.split()

    float_lat = float(parameters[0])
    float_lng = float(parameters[1])
    float_alt = float(parameters[2])

    if cs.mode == 'MANUAL': #Safety Manual Mode Switch
        Script.ChangeMode("Manual")
        break
    else:
        #waypoint creation
        item = MissionPlanner.Utilities.Locationwp() # creating waypoint
        MissionPlanner.Utilities.Locationwp.lat.SetValue(item,float_lat)
        MissionPlanner.Utilities.Locationwp.lng.SetValue(item,float_lng)
        MissionPlanner.Utilities.Locationwp.alt.SetValue(item,float_alt)
        MAV.setGuidedModeWP(item) #set waypoint

        print("Waypoint set at lat: {:} lng: {:} alt: {:}".format(float_lat, float_lng, float_alt))
    
    #timing
    time.sleep(1)

# exit
rsock.close()
print("Script End")
