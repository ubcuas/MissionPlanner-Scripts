#Python 2.7

import socket
import struct
import time
from datetime import datetime
import clr
clr.AddReference("MissionPlanner.Utilities")
import MissionPlanner
clr.AddReference("MissionPlanner.Utilities") # Includes the Utilities class
from MissionPlanner.Utilities import Locationwp
clr.AddReference("MAVLink")
import MAVLink

HOST = 'localhost' # Symbolic name meaning all available interfaces
#SPORT = 5000 # Arbitrary non-privileged port  
RPORT = 9001 # Arbitrary non-privileged port

DELAY = 1 # Seconds

REMOTE = ''
# Datagram (udp) socket 

MODE = "plane"
ALTSTD = MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT

rsock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
timeout = 5
rsock.settimeout(timeout)
print("Sockets Created")

wp_array = []
upcoming_mission = False
fence_exclusive = False
fence_type = ""

def get_altitude_standard(standard):
    if standard == "AGL":
        return MAVLink.MAV_FRAME.GLOBAL_RELATIVE_ALT
    else:
        return MAVLink.MAV_FRAME.GLOBAL

def command_to_MAV_CMD(command):
    temp_dict = {
        0 : MAVLink.MAV_CMD.WAYPOINT,
        1 : MAVLink.MAV_CMD.LOITER_UNLIM,
        2 : MAVLink.MAV_CMD.DO_VTOL_TRANSITION,
    }
    return temp_dict[command]

def upload_mission(wp_array):
    """
    Uploads a mission to the aircraft based on a given set of waypoints.

    Parameters:
        - wp_array: ordered list of waypoints
    """
    #start = time.monotonic_ns()
    # Set waypoint total
    MAV.setWPTotal(len(wp_array) + 1)
    # Upload waypoints
    dummy = Locationwp()
    Locationwp.lat.SetValue(dummy, 0)
    Locationwp.lng.SetValue(dummy, 0)
    Locationwp.alt.SetValue(dummy, 0)
    Locationwp.id.SetValue(dummy, int(MAVLink.MAV_CMD.WAYPOINT))
    MAV.setWP(dummy, 0, ALTSTD)
    for i in range(0, len(wp_array)):
        wp = Locationwp()
        Locationwp.lat.SetValue(wp, wp_array[i][0])
        Locationwp.lng.SetValue(wp, wp_array[i][1])
        Locationwp.alt.SetValue(wp, wp_array[i][2])
        Locationwp.id.SetValue(wp, int(command_to_MAV_CMD(wp_array[i][3])))
        MAV.setWP(wp, i + 1, ALTSTD)
    # Final ack
    MAV.setWPACK()
    #end = time.monotonic_ns()
    #print("Uploading mission took {:}ms".format((end - start) / 1000000))

def interpret_normal(recvd):
    msg = recvd.decode()
    return msg.split()

def interpret_packedmission(recvd):
    ret = ["NEXT"]

    #print(recvd)
    for i in range(len(recvd) // 4):
        idx = 4 * i
        #print(recvd[idx:idx + 8])
        ret.append(struct.unpack('f', recvd[idx:idx + 4])[0])

    #print(ret)
    return ret

# Keep talking with the Mission Planner server 
while 1:

    # Send telemetry to server
    location = "telemetry {:} {:} {:} {:} {:} {:} {:} {:} {:} {:} {:} {:} {:}".format(cs.lat, cs.lng, cs.alt, cs.roll, cs.pitch, cs.yaw, cs.airspeed, cs.groundspeed, cs.battery_voltage, cs.wpno, cs.wind_dir, cs.wind_vel, str(datetime.now()))
    rsock.sendto(bytes(location, 'utf-8'), (HOST, RPORT))

    #print("Waypoint Count", MAV.getWPCount())

    try:
        recvd = rsock.recv(4096)
        #print("received {:} bytes".format(len(recvd)))
    except socket.timeout:
        print("Socket timeout")
        time.sleep(DELAY)
        continue
    except socket.error as e:
        print(e)
        print("Socket error - trying again in 10 seconds...")
        # MissionPlanner.MainV2.speechEngine.SpeakAsync("Socket connection error. Trying again in 10 seconds. skill issue")
        time.sleep(10)
        continue

    if (upcoming_mission):
        argv = interpret_packedmission(recvd)
    else:
        argv = interpret_normal(recvd)

    cmd = argv.pop(0)
    
    if cs.mode == 'MANUAL': # Safety Manual Mode Switch
        print("Entered Manual Mode")
        break
    else:
        if cmd == "NEW_MISSION":
            #Enter guided and await new mission waypoints
            wp_array = []
            upcoming_mission = True
            print("NEW_MISSION - About to recieve new mission")

        elif cmd == "NEXT":
            upcoming_mission = False

            print(cmd, argv)

            if (len(argv) % 4 != 0):
                print("recieved {:} waypoint params, not divisible by 4".format(len(argv)))

            for idx in range(0, len(argv) // 4):
                float_lat = float(argv[4 * idx])
                float_lng = float(argv[4 * idx + 1])
                float_alt = float(argv[4 * idx + 2])
                command = int(argv[4 * idx + 3])

                wp_array.append((float_lat, float_lng, float_alt, command))
                print("received waypoint {:} {:} {:}".format(float_lat, float_lng, float_alt))
            
            #set mission
            upload_mission(wp_array)
            # Empty array
            wp_array = []
            # Quickly switch out of Auto mode so drone recognizes new mission
            #Script.ChangeMode("Loiter") #Uncomment for testing May 12
            Script.ChangeMode("Auto")
            print("NEXT - new mission set")   
        
        elif cmd == "PUSH":
            wptotal = MAV.getWPCount()

            MAV.setWPTotal(wptotal + 1)
            # Upload waypoints
            newwp = Locationwp()
            Locationwp.lat.SetValue(newwp, float(argv[0]))
            Locationwp.lng.SetValue(newwp, float(argv[1]))
            Locationwp.alt.SetValue(newwp, float(argv[2]))
            Locationwp.id.SetValue(newwp, int(MAVLink.MAV_CMD.WAYPOINT))
            MAV.setWP(newwp, wptotal, ALTSTD)
            MAV.setWPACK()

            # Quickly switch out of Auto mode so drone recognizes new mission
            #Script.ChangeMode("Loiter") #Uncomment for testing May 12
            Script.ChangeMode("Auto")

            print("PUSH - waypoint pushed")
        
        elif cmd == "CONT":
            # CONT - continue
            #print("CONT")
            pass

        elif cmd == "IDLE":
            # IDLE - do nothing
            #print("IDLE")
            pass

        elif cmd == "TAKEOFF":
            if (len(argv) != 1):
                print("TAKEOFF - invalid command")

                rsock.sendto(bytes("success_takeoff 0", 'utf-8'), (HOST, RPORT))
            else:
                takeoffalt = float(argv[0])
                # Set up takeoff waypoint
                # NOTE: drone can't be in Auto on the ground when sending the initial takeoff mission - if it is, it won't take off
                # May 12 testing - verify if this is the behaviour on the actual drone - if so, we may consider switching the mode
                # to something safe like 'loiter' here just in case
                home = Locationwp()
                Locationwp.id.SetValue(home, int(MAVLink.MAV_CMD.WAYPOINT))
                Locationwp.lat.SetValue(home, cs.lat)
                Locationwp.lng.SetValue(home, cs.lng)
                Locationwp.alt.SetValue(home, 0)
                
                takeoff = Locationwp()
                Locationwp.id.SetValue(takeoff, int(MAVLink.MAV_CMD.VTOL_TAKEOFF) if MODE == "plane" else int(MAVLink.MAV_CMD.TAKEOFF))
                Locationwp.lat.SetValue(takeoff, cs.lat)
                Locationwp.lng.SetValue(takeoff, cs.lng)
                Locationwp.alt.SetValue(takeoff, takeoffalt)

                loiter_unlim = Locationwp()
                Locationwp.id.SetValue(loiter_unlim, int(MAVLink.MAV_CMD.LOITER_UNLIM))
                Locationwp.lat.SetValue(loiter_unlim, cs.lat)
                Locationwp.lng.SetValue(loiter_unlim, cs.lng)
                Locationwp.alt.SetValue(loiter_unlim, 0)

                MAV.setWPTotal(3)
                MAV.setWP(home,0,ALTSTD)
                MAV.setWP(takeoff,1,ALTSTD)
                MAV.setWP(loiter_unlim,2,ALTSTD)
                MAV.setWPACK()

                DELAY_SECONDS = 15
                for i in range(0, DELAY_SECONDS * 10):
                    if cs.mode == "AUTO":
                        break
                    time.sleep(0.1)

                if cs.mode == "AUTO":
                    #take off
                    print("TAKEOFF - takeoff to {:}m".format(takeoffalt))
                    rsock.sendto(bytes("success_takeoff 1", 'utf-8'), (HOST, RPORT))
                else:
                    print("TAKEOFF - ERROR, MODE NOT AUTO")
                    rsock.sendto(bytes("success_takeoff 0", 'utf-8'), (HOST, RPORT))


        elif cmd == "HOME":
            MAV.doCommand(MAVLink.MAV_CMD.DO_SET_HOME,0,0,0,0,float(argv[0]),float(argv[1]),float(argv[2]))
            print("HOME - set a new home")
        
        elif cmd == "ARM":
            MAV.doCommand(MAVLink.MAV_CMD.COMPONENT_ARM_DISARM, int(argv[0]), 0, 0, 0, 0, 0, 0, 0)
            print("ARM - arm/disarm motors")
            
            #cs.armed can take some time to change - give it time before we consider it failed
            DELAY_SECONDS = 3
            for i in range(0, DELAY_SECONDS * 10):
                #print("{:.1f}".format(i * 0.1), cs.armed)
                if cs.armed == (int(argv[0]) == 1):
                    break
                time.sleep(0.1)

            if cs.armed == (int(argv[0]) == 1):
                rsock.sendto(bytes("success_arm 1", 'utf-8'), (HOST, RPORT))
            else:
                rsock.sendto(bytes("success_arm 0", 'utf-8'), (HOST, RPORT))

        elif cmd == "RTL":
            rtl_altitude = float(argv[0]) * 100
            if MODE == 'plane':
                MAV.setParam('ALT_HOLD_RTL', rtl_altitude)
                Script.ChangeMode("QRTL")
            else:
                MAV.setParam('RTL_ALT', rtl_altitude)
                Script.ChangeMode("RTL")
            
            print("RTL - returning to launch")

        elif cmd == "LAND":
            MAV.doCommand(MAVLink.MAV_CMD.LAND,0,0,0,0,cs.lat,cs.lng,0)
            print("LAND - landing in place")
        
        elif cmd == "VTOL_LAND":
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
            Locationwp.alt.SetValue(landing, 0)

            MAV.setWPTotal(2)
            MAV.setWP(home,0,ALTSTD)
            MAV.setWP(landing,1,ALTSTD)
            MAV.setWPACK()
            Script.ChangeMode("Auto")
            # MAV.doCommand(MAVLink.MAV_CMD.LAND,0,0,0,0,cs.lat,cs.lng,0)
            print("VTOL_LAND - landing at {:}, {:}".format(landlat, landlng))
        
        elif cmd == "MODE":
            MAV.doCommand(MAVLink.MAV_CMD.DO_VTOL_TRANSITION,int(argv[0]),0,0,0,0,0,0)
        
        elif cmd == "FLIGHT_MODE":
            if MODE == 'plane' and argv[0] in ['loiter', 'stabilize']:
                Script.ChangeMode("q{:}".format(argv[0]))
            else:
                Script.ChangeMode(argv[0])

        elif cmd == "QUEUE_GET":
            #get info
            numwp = MAV.getWPCount()
            wplist = []
            for i in range(0, numwp):
                try:
                    wp = MAV.getWP(MAV.sysidcurrent, MAV.compidcurrent, i)
                    wplist.append((wp.lat, wp.lng, wp.alt))
                except:
                    pass
            #send info
            queue_info = "queue {:}".format(numwp)
            for wp in wplist:
                queue_info += " {:} {:} {:}".format(wp[0], wp[1], wp[2])

            rsock.sendto(bytes(queue_info, 'utf-8'), (HOST, RPORT))
        
        elif cmd == "CONFIG":
            if argv[0] in ["vtol", "plane"]:
                MODE = argv[0]
        
        elif cmd == "ALTSTD":
            ALTSTD = get_altitude_standard(argv[0])

        else:
            print("unrecognized command", cmd, argv)

    #timing
    time.sleep(DELAY)

# exit
rsock.close()
print("Script End")