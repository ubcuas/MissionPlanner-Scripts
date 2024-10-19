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
    ("WAYPOINT",  16),
    ("LOITER_UNLIM",  17),
    ("LOITER_TURNS",  18),
    ("LOITER_TIME",  19),
    ("LOITER_TO_ALT",  31),
    ("RETURN_TO_LAUNCH",  20),
    ("LAND",  21),
    ("TAKEOFF",  22),
    ("VTOL_TAKEOFF",  84),
    ("VTOL_LAND",  85),
    ("PAYLOAD_PLACE",  94),
    ("SCRIPT_TIME",  42702),
    ("DO_SEND_SCRIPT_MESSAGE",  217),
    ("DO_VTOL_TRANSITION",  3000),
    ("IMAGE_START_CAPTURE",  2000),
    ("IMAGE_STOP_CAPTURE",  2001),
    ("SET_CAMERA_ZOOM",  531),
    ("SET_CAMERA_FOCUS",  532),
    ("VIDEO_START_CAPTURE",  2500),
    ("VIDEO_STOP_CAPTURE",  2501),
    ("DO_AUX_FUNCTION",  218),
    ("ALTITUDE_WAIT",  83),
    ("CONTINUE_AND_CHANGE_ALT",  30),
    ("CONDITION_DELAY",  112),
    ("CONDITION_DISTANCE",  114),
    ("CONDITION_YAW",  115),
    ("DO_GRIPPER",  211),
    ("DO_LAND_START",  189),
    ("DO_SET_ROI",  201),
    ("DO_INVERTED_FLIGHT",  210),
    ("DO_SET_CAM_TRIGG_DIST",  206),
    ("DO_JUMP",  177),
    ("JUMP_TAG",  600),
    ("DO_JUMP_TAG",  601),
    ("DO_CHANGE_SPEED",  178),
    ("DO_SET_HOME",  179),
    ("DO_SET_RELAY",  181),
    ("DO_REPEAT_RELAY",  182),
    ("DO_SET_SERVO",  183),
    ("DO_REPEAT_SERVO",  184),
    ("DO_DIGICAM_CONFIGURE",  202),
    ("DO_DIGICAM_CONTROL",  203),
    ("DO_MOUNT_CONTROL",  205),
    ("DO_GIMBAL_MANAGER_PITCHYAW",  1000),
    ("DO_PARACHUTE",  208),
    ("DO_FENCE_ENABLE",  207),
    ("DO_SPRAYER",  216),
    ("DO_AUTOTUNE_ENABLE",  212),
    ("DO_ENGINE_CONTROL",  223),
    ("DO_SET_RESUME_REPEAT_DIST",  215)
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
