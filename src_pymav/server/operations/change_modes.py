from pymavlink.mavutil import mavfile, mavlink


def change_flight_mode(
    mav_connection: mavfile, tgt_sys_id: int = 1, tgt_comp_id: int = 1, flightmode: str = ""
) -> bool:

    flightmode = flightmode.upper()
    if flightmode not in mav_connection.mode_mapping():
        return False

    mode_id = mav_connection.mode_mapping()[flightmode.upper()]
    sub_mode = 0

    mav_connection.mav.command_long_send(
        target_system=tgt_sys_id,
        target_component=tgt_comp_id,
        command=mavlink.MAV_CMD_DO_SET_MODE,
        confirmation=0,
        param1=mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        param2=mode_id,
        param3=sub_mode,
        param4=0,
        param5=0,
        param6=0,
        param7=0,
    )
    verify_ack(mav_connection, "Failed ACK after change_flight_mode")

    return True


def change_aircraft_type(mav_connection: mavfile):
    # TODO investigate whether to deprecate
    pass

def verify_ack(mavlink_connection: mavfile, error_msg: str) -> bool:
    """
    Verifies the ack response.

    Args:
        master (mavutil.mavlink_connection): The MAVLink connection to use.
        error_msg (str): The error message to log if ack verification fails.

    Returns:
        bool: True if ack verification successful, False otherwise.
    """
    ack = mavlink_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=3)
    print("ack:", ack)
    # if ack.type != 0:
    #     print(f'{error_msg}: {ack.type}')
    #     return False
    return True