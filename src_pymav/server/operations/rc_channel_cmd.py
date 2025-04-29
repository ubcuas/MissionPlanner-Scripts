import math

from pymavlink import mavutil

from server.common.status import Status
from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.encoders import command_int_to_string
from server.utilities.request_message_streaming import request_messages

"""
    Sends a specified value to the drone's RC channels.
    @input mav_connection: The MAVLink connection object.
    @input channel: The channel number to send the value to.
        Value between 1 and 18, inclusive.
        NOTE: channel 5 and 8 is used for flight mode, DO NOT use these channels.
    @input value: The value to send to the specified channel. 
        Normally 1000 ~ 2000, 0 to release channel back to the RC radio, 
        UINT16_MAX (e.g 65535) to ignore this field 

    NOTE: Parameter RC_OVERRIDE_TIME should be set to -1 (so overrides never expire)
"""
def send_rc_channel_value(mav_connection: mavutil.mavfile, channel: int, value: int, 
                          tgt_sys_id: int = 1, tgt_comp_id: int = 1, timeout = 10) -> int:
    if channel < 1 or channel > 18:
        print(f"Channel {channel} is out of range. Must be between 1 and 18, inclusive.")
        return -1
    if channel == 5 or channel == 8:
        print(f"Channel {channel} is used for flight mode. Do not use this channel.")
        return -1
    if value < 0 or value > 65535:
        print(f"Value {value} is out of range. Must be between 0 and 65535, inclusive.")
        return -1
    
    channel_values = [0] * 18
    channel_values[channel - 1] = value

    print(f"DEBUG: channel_values: {channel_values}")

    result = mav_connection.mav.rc_channels_override_send(
        mav_connection.target_system,
        mav_connection.target_component,
        *channel_values
    )

    print(f"RC Channel value of {value} sent to channel {channel} successfully.")
    return 1


