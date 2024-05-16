import struct

from server.common.wpqueue import Waypoint

# TODO: We can consider replacing this with a better datastructure in the future.
# We're looking for something that's kind of like a two-way dictionary, since
# the relation here is bijective.
#
# NOTE: it is EXTREMELY important that the integer mappings here correspond
# EXACTLY with the values of MissionPlanner's MAV_CMD enums. 
# https://mavlink.io/en/messages/common.html#mav_commands <- number in parentheses next to waypoint is the enum value.
# https://github.com/ArduPilot/MissionPlanner/blob/master/Resources/MAVCmd.txt
command_mappings: list[tuple[str, int]] = [
    ("WAYPOINT", 16),
    ("LOITER_UNLIM", 17),
    ("DO_VTOL_TRANSITION", 3000),
    ("DO_CHANGE_SPEED", 178)
]

def command_string_to_int(command: str) -> int:
    for pair in command_mappings:
        if pair[0] == command:
            return pair[1]
    return 16 #Default

def command_int_to_string(command: int) -> str:
    for pair in command_mappings:
        if pair[1] == command:
            return pair[0]
    return "WAYPOINT" #Default

def waypoint_encode(wp: Waypoint) -> bytes:
    return struct.pack("3f5h", 
                       wp._lat, 
                       wp._lng, 
                       wp._alt, 
                       command_string_to_int(wp._com),
                       wp._param1, 
                       wp._param2, 
                       wp._param3, 
                       wp._param4)

def waypoint_decode(wp: bytes) -> Waypoint:
    latitude, longitude, altitude, command_int, param1, param2, param3, param4 = struct.unpack("3f5h", wp)
    return Waypoint("", "", 
                    latitude, 
                    longitude, 
                    altitude, 
                    command_int_to_string(command_int), 
                    param1,
                    param2,
                    param3,
                    param4)

def waypoint_size() -> int:
    return struct.calcsize('3f5h')
