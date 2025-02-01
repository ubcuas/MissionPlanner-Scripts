from pymavlink import mavutil

# return value of 0 indicates success
def land_in_place(mavlink_connection: mavutil.mavlink_connection, timeout: int = 10) -> int:
    # Send a land command
    mavlink_connection.mav.command_long_send(
        mavlink_connection.target_system,
        mavlink_connection.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, 0, 0, 0
    )

    # Wait for the acknowledgment
    ack = mavlink_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1

    return ack.result

# return value of 0 indicates success
def land_at_position(mavlink_connection: mavutil.mavlink_connection, latitude: float, longitude: float, timeout: int = 10) -> int:
    # Send a land command
    mavlink_connection.mav.command_long_send(
        mavlink_connection.target_system,
        mavlink_connection.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND,
        0, 0, 0, 0, 0, latitude, longitude, 0
    )

    # Wait for the acknowledgment
    ack = mavlink_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1

    print(f"land at position command ack: {ack}")

    return ack.result
