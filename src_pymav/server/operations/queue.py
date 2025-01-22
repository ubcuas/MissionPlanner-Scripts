from pymavlink import mavutil

from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.encoders import command_string_to_int, command_int_to_string

def set_home(mavlink_connection: mavutil.mavlink_connection, latitude: float, longitude: float, altitude: float): # -> int | None:
    # Send a set home command
    mavlink_connection.mav.command_long_send(
        mavlink_connection.target_system,
        mavlink_connection.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_HOME,
        0, 0, 0, 0, 0, latitude, longitude, altitude
    )

    # Wait for the acknowledgment
    ack = mavlink_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return None

    return ack.result

def new_mission(mavlink_connection: mavutil.mavlink_connection, waypoint_queue: WaypointQueue) -> bool:
    # Clear any existing mission from vehicle
    print('Clearing mission')
    mavlink_connection.mav.mission_clear_all_send(mavlink_connection.target_system, mavlink_connection.target_component)

    if not verify_ack(mavlink_connection, 'Error clearing mission'):
        return False
    
    # Insert the home waypoint
    wp_list = []
    seq = 0
    wp_list.append(mavutil.mavlink.MAVLink_mission_item_int_message(
        0, 0, seq, 0, 16, 0, 0, 0, 0, 0, 0,
        0, 
        0, 
        0
    ))
    
    # Insert the rest of the waypoints
    for seq in range(1, len(waypoint_queue) + 1):
        wp: Waypoint = waypoint_queue[seq - 1]

        wp_list.append(mavutil.mavlink.MAVLink_mission_item_int_message(
        mavlink_connection.target_system, mavlink_connection.target_component, seq, 
        0, command_string_to_int(wp._com), 0, 1, 
        float(wp._param1), float(wp._param2), float(wp._param3), 
        float(wp._param4), int(wp._lat * 10000000), int(wp._lng * 10000000), 
        int(wp._alt)
    ))

    # Send waypoint count to the UAV
    mavlink_connection.waypoint_count_send(len(wp_list))

    # Upload waypoints to the UAV
    return send_waypoints(mavlink_connection, wp_list)

def send_waypoints(mavlink_connection: mavutil.mavlink_connection, wp_list: list) -> bool:
    """
    Send the waypoints to the UAV.

    Args:
        master (mavutil.mavlink_connection): The MAVLink connection to use.
        wploader (list): The waypoint loader list.

    Returns:
        bool: True if waypoints are successfully sent, False otherwise.
    """
    for i in range(len(wp_list)):
        msg = mavlink_connection.recv_match(type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'], blocking=True, timeout=3)
        if not msg:
            print('No waypoint request received')
            return False
        print(f'Sending waypoint {msg.seq}/{len(wp_list)-1}')
        mavlink_connection.mav.send(wp_list[msg.seq])

        if msg.seq == len(wp_list)-1:
            break

    return verify_ack(mavlink_connection, 'Error uploading mission')

def verify_ack(mavlink_connection: mavutil.mavlink_connection, error_msg: str) -> bool:
    """
    Verifies the ack response.

    Args:
        master (mavutil.mavlink_connection): The MAVLink connection to use.
        error_msg (str): The error message to log if ack verification fails.

    Returns:
        bool: True if ack verification successful, False otherwise.
    """
    ack = mavlink_connection.recv_match(type='MISSION_ACK', blocking=True, timeout=3)
    print(ack)
    if ack is None or ack.type != 0:
        print(f'{error_msg}: {ack.type}')
        return False
    return True

def clear_mission(mavlink_connection: mavutil.mavlink_connection) -> bool:
    mavlink_connection.mav.mission_clear_all_send(
        mavlink_connection.target_system,
        mavlink_connection.target_component,
        mavutil.mavlink.MAV_MISSION_TYPE_MISSION
    )

    return verify_ack(mavlink_connection, "")

def insert_wp():
    pass

