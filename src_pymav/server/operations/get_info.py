import math

from pymavlink import mavutil

from server.common.status import Status
from server.utilities.request_message_streaming import request_messages

"""
    Get current status of a drone
    Type of message can be found on https://mavlink.io/en/messages/common.html

"""
def get_status(mav_connection: mavutil.mavfile) -> Status:

    # trigger an update
    mav_connection.recv_match(blocking=True)
    request_messages(mav_connection, [
        mavutil.mavlink.MAVLINK_MSG_ID_SYSTEM_TIME, # seems like only one is needed
        # mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 
        # mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE,
        # mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD,
        # mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS,
        # mavutil.mavlink.MAVLINK_MSG_ID_MISSION_ITEM_REACHED,
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

    status_wpn = mav_connection.messages.get('MISSION_ITEM_REACHED', Object(seq = 0))
    latency_wpn = mav_connection.time_since('MISSION_ITEM_REACHED')

    status_wind = mav_connection.messages.get('WIND_COV', Object(wind_x = 0, wind_y = 0))
    latency_wind = mav_connection.time_since('WIND_COV')

    print(latency_time, latency_gps, latency_att, latency_vfr, latency_sys, latency_wpn, latency_wind)

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

def get_current_mission():
    pass