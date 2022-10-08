import math
import socketserver

from missions import Waypoint, Mission

#create a test mission
test_mission = Mission()
test_mission.add_wp(Waypoint(-35.3627798, 149.1651830, 10))
test_mission.add_wp(Waypoint(-35.3631439, 149.1647033, 10))
test_mission.add_wp(Waypoint(-35.3637428, 149.1647949, 10))
test_mission.add_wp(Waypoint(-35.3638713, 149.1659743, 10))

class UDPHandler(socketserver.BaseRequestHandler):
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

        print(f"Current Location: lat: {current_lat} lng: {current_lng} alt: {current_alt}")
        current_wp = Waypoint(current_lat, current_lng, current_alt)

        #check if current mission has completed
        if (test_mission.mission_complete()):
            socket.sendto(bytes("IDLE 0 0 0", "utf-8"), self.client_address)
        else:
            #check progress
            if (test_mission.mission_check_wp(current_wp)):
                print("Waypoint Reached!")

            #send waypoint to UAV
            socket.sendto(bytes("NEXT " + str(test_mission.mission_current_wp()), "utf-8"), self.client_address)

if __name__ == "__main__":
    HOST, PORT = "localhost", 4000
    server = socketserver.UDPServer((HOST, PORT), UDPHandler)
    server.serve_forever()  
