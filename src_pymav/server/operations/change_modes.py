from pymavlink.mavutil import mavfile

# TODO: Should we be referring to pymavlink.dialects.v10.cubepilot here?
from pymavlink.dialects.v10.ardupilotmega import MAVLink
from pymavlink.dialects.v10 import ardupilotmega as dialect


def change_flight_mode(
    mav_connection: mavfile, tgt_sys_id: int = 1, tgt_comp_id: int = 1, flightmode: str = ""
):
    flightmode_lookup = {
        # "loiter": dialect.MAV_MODE_LOITER,
        "stabilize": dialect.MAV_MODE_STABILIZE_ARMED,
        "auto": dialect.MAV_MODE_AUTO_ARMED,
        "guided": dialect.MAV_MODE_GUIDED_ARMED,
    }

    link: MAVLink = mav_connection.mav
    link.command_long_send(
        target_system=tgt_sys_id,
        target_component=tgt_comp_id,
        command=dialect.MAV_CMD_DO_SET_MODE,
        confirmation=0,
        param1=flightmode_lookup[flightmode],
        param2=0,
        param3=0,
        param4=0,
        param5=0,
        param6=0,
        param7=0,
    )
    print(verify_ack(mav_connection, "test"))


def change_aircraft_type(mav_connection: mavfile):
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
    print(ack)
    # if ack.type != 0:
    #     print(f'{error_msg}: {ack.type}')
    #     return False
    return True