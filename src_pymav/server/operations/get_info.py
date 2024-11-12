from pymavlink import mavutil

"""
    Get current status of a drone
    Type of message can be found on https://mavlink.io/en/messages/common.html

"""
def get_status(mav_connection) -> dict:
    status = {}
    # This doesn't seems to get all message
    # status_msg = mav_connection.recv_match(type=['GLOBAL_POSITION_INT', 'ATTITUDE', 'VFR_HUD', 'SYS_STATUS'], blocking=True)
    status_gps = mav_connection.recv_match(type=['GLOBAL_POSITION_INT'], blocking=True)
    # TODO: Investigate timestamp since different message come at different time
    status["timestamp"] = status_gps.time_boot_ms
    status["current_wpn"] = 0 # TODO
    status["latitude"] = status_gps.lat
    status["longitude"] = status_gps.lon
    status["altitude"] = status_gps.alt # TODO: Check which alt to use
    status_alt = mav_connection.recv_match(type=['ATTITUDE'], blocking=True)
    status["roll"] = status_alt.roll
    status["pitch"] = status_alt.pitch
    status["yaw"] = status_alt.yaw
    status_vfr = mav_connection.recv_match(type=['VFR_HUD'], blocking=True)
    status["airspeed"] = status_vfr.airspeed
    status["groundspeed"] = status_vfr.groundspeed
    status["heading"] = status_vfr.heading
    status_sys = mav_connection.recv_match(type=['SYS_STATUS'], blocking=True)
    status["batteryvoltage"] = status_sys.voltage_battery
    status["winddirection"] = 0 # TODO
    status["windvelocity"] = 0 # TODO

    
    return status

def get_current_mission():
    pass