import math

from pymavlink import mavutil

from server.common.status import Status
from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.encoders import command_int_to_string
from server.utilities.request_message_streaming import request_messages

"""
    Get current status of a drone
    Type of message can be found on https://mavlink.io/en/messages/common.html

"""
def get_status(mav_connection: mavutil.mavfile) -> Status:

    # trigger an update
    # mav_connection.recv_match(blocking=True)
    request_messages(mav_connection, [
        mavutil.mavlink.MAVLINK_MSG_ID_SYSTEM_TIME, # seems like only one is needed
        # mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 
        # mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE,
        # mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD,
        # mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS,
        # mavutil.mavlink.MAVLINK_MSG_ID_MISSION_CURRENT,
        # mavutil.mavlink.MAVLINK_MSG_ID_WIND_COV,
    ])

    # use the mav_connection.messages dictionary to access the most recent messages of a particular type

    Object = lambda **kwargs: type("Object", (), kwargs)

    system_time = mav_connection.messages.get('SYSTEM_TIME', Object(time_unix_usec = 0, time_boot_ms = 0))
    latency_time = mav_connection.time_since('SYSTEM_TIME')

    status_gps = mav_connection.messages.get('GLOBAL_POSITION_INT', Object(lat = 0, lon = 0, alt = 0))
    latency_gps = mav_connection.time_since('GLOBAL_POSITION_INT')

    status_att = mav_connection.messages.get('ATTITUDE', Object(roll = 0, pitch = 0, yaw = 0))
    latency_att = mav_connection.time_since('ATTITUDE')

    status_vfr = mav_connection.messages.get('VFR_HUD', Object(airspeed = 0, groundspeed = 0, climb = 0))
    latency_vfr = mav_connection.time_since('VFR_HUD')

    status_sys = mav_connection.messages.get('SYS_STATUS', Object(voltage_battery = 0))
    latency_sys = mav_connection.time_since('SYS_STATUS')

    status_wpn = mav_connection.messages.get('MISSION_CURRENT', Object(seq = 0, total = 0, mission_state = 0, mission_mode = 0, mission_id = 0))
    latency_wpn = mav_connection.time_since('MISSION_CURRENT')

    status_wind = mav_connection.messages.get('WIND_COV', Object(wind_x = 0, wind_y = 0))
    latency_wind = mav_connection.time_since('WIND_COV')

    print(f"Latencies: {latency_time:2f}s, {latency_gps:2f}s, {latency_att:2f}s, {latency_vfr:2f}s, {latency_sys:2f}s, {latency_wpn:2f}s, {latency_wind:2f}s")

    # wind calculations in the horizontal plane TODO determine if vertical windspeed is needed
    winddirection = math.degrees(math.atan(status_wind.wind_x / status_wind.wind_y)) if status_wind.wind_y != 0 else (0 if status_wind.wind_x > 0 else 180)
    windvelocity = math.sqrt(status_wind.wind_x * status_wind.wind_x + status_wind.wind_y * status_wind.wind_y)

    return Status(
        system_time.time_unix_usec / 1000000, # seconds

        status_wpn.seq,

        status_gps.lat / 10000000,
        status_gps.lon / 10000000,
        status_gps.alt / 1000, # meters

        status_att.roll,
        status_att.pitch,
        status_att.yaw,

        status_vfr.airspeed,
        status_vfr.groundspeed,
        status_vfr.climb,

        status_sys.voltage_battery,

        winddirection,
        windvelocity
    )

def get_current_mission(mav_connection: mavutil.mavfile) -> WaypointQueue:

    ret = WaypointQueue()

    mav_connection.mav.mission_request_list_send(
        mav_connection.target_system, 
        mav_connection.target_component,
        mavutil.mavlink.MAV_MISSION_TYPE_MISSION
    )

    msg = mav_connection.recv_match(type=['MISSION_COUNT'], blocking=True)
    if msg and msg.get_type() != "BAD_DATA":
        print(f"Recieved {msg}")

    # use MISSION_REQUEST_INT for all mission items
    for current in range(msg.count):
        msg = mav_connection.mav.mission_request_int_send(
            mav_connection.target_system,
            mav_connection.target_component,
            current,
            mavutil.mavlink.MAV_MISSION_TYPE_MISSION
        )

        # receive MISSION_ITEM_INT
        msg = mav_connection.recv_match(type=['MISSION_ITEM_INT'], blocking=True)
        if msg and msg.get_type() != "BAD_DATA":
            # print(f"Recieved the {current}th Mission Item: {msg}")
        
            ret.push(Waypoint(0, f"Mission Waypoint {msg.seq}" if msg.seq != 0 else "Home Waypoint", 
                            msg.x / 10000000,
                            msg.y / 10000000,
                            msg.z,
                            command_int_to_string(msg.command),
                            msg.param1,
                            msg.param2,
                            msg.param3,
                            msg.param4))
        else: 
            ret.push(Waypoint(name=f"Error reading waypoint {current}"))

    return ret