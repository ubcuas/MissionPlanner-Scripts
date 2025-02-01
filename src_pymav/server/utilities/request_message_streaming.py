from pymavlink import mavutil

def set_message_streaming_rates(connection):
    GPS_RATE_HZ = 0.25
    ATTITUDE_RATE_HZ = 1
    VFR_HUD_RATE_HZ = 1
    SYS_STATUS_RATE_HZ = 5
    MISSION_ITEM_REACHED_RATE_HZ = 1
    WIND_COV_RATE_HZ = 10

    message = connection.mav.command_long_encode(
        connection.target_system,  # Target system ID
        connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,  # param1: Message ID to be streamed
        int(GPS_RATE_HZ * 1000000), # param2: Interval in microseconds
        0,       # param3 (unused)
        0,       # param4 (unused)
        0,       # param5 (unused)
        0,       # param6 (unused)
        2        # param7: Response Target: (2 - broadcast)
    )
    
    connection.mav.send(message)

    response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    if (response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED):
        print(f"Setting {GPS_RATE_HZ = } Hz")
    else:
        print(f"Setting {GPS_RATE_HZ = } failed")

    message = connection.mav.command_long_encode(
        connection.target_system,  # Target system ID
        connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE,  # param1: Message ID to be streamed
        int(ATTITUDE_RATE_HZ * 1000000), # param2: Interval in microseconds
        0,       # param3 (unused)
        0,       # param4 (unused)
        0,       # param5 (unused)
        0,       # param6 (unused)
        2        # param7: Response Target: (2 - broadcast)
    )
    
    connection.mav.send(message)

    response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    if (response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED):
        print(f"Setting {ATTITUDE_RATE_HZ = } Hz")
    else:
        print(f"Setting {ATTITUDE_RATE_HZ = } failed")
    
    message = connection.mav.command_long_encode(
        connection.target_system,  # Target system ID
        connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_VFR_HUD,  # param1: Message ID to be streamed
        int(VFR_HUD_RATE_HZ * 1000000), # param2: Interval in microseconds
        0,       # param3 (unused)
        0,       # param4 (unused)
        0,       # param5 (unused)
        0,       # param6 (unused)
        2        # param7: Response Target: (2 - broadcast)
    )
    
    connection.mav.send(message)

    response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    if (response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED):
        print(f"Setting {VFR_HUD_RATE_HZ = } Hz")
    else:
        print(f"Setting {VFR_HUD_RATE_HZ = } failed")

    message = connection.mav.command_long_encode(
        connection.target_system,  # Target system ID
        connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_SYS_STATUS,  # param1: Message ID to be streamed
        int(SYS_STATUS_RATE_HZ * 1000000), # param2: Interval in microseconds
        0,       # param3 (unused)
        0,       # param4 (unused)
        0,       # param5 (unused)
        0,       # param6 (unused)
        2        # param7: Response Target: (2 - broadcast)
    )
    
    connection.mav.send(message)

    response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    if (response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED):
        print(f"Setting {SYS_STATUS_RATE_HZ = } Hz")
    else:
        print(f"Setting {SYS_STATUS_RATE_HZ = } failed")
    
    message = connection.mav.command_long_encode(
        connection.target_system,  # Target system ID
        connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_MISSION_ITEM_REACHED,  # param1: Message ID to be streamed
        int(MISSION_ITEM_REACHED_RATE_HZ * 1000000), # param2: Interval in microseconds
        0,       # param3 (unused)
        0,       # param4 (unused)
        0,       # param5 (unused)
        0,       # param6 (unused)
        2        # param7: Response Target: (2 - broadcast)
    )
    
    connection.mav.send(message)

    response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    if (response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED):
        print(f"Setting {MISSION_ITEM_REACHED_RATE_HZ = } Hz")
    else:
        print(f"Setting {MISSION_ITEM_REACHED_RATE_HZ = } failed")
    
    message = connection.mav.command_long_encode(
        connection.target_system,  # Target system ID
        connection.target_component,  # Target component ID
        mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,  # ID of command to send
        0,  # Confirmation
        mavutil.mavlink.MAVLINK_MSG_ID_WIND_COV,  # param1: Message ID to be streamed
        int(WIND_COV_RATE_HZ * 1000000), # param2: Interval in microseconds
        0,       # param3 (unused)
        0,       # param4 (unused)
        0,       # param5 (unused)
        0,       # param6 (unused)
        2        # param7: Response Target: (2 - broadcast)
    )
    
    connection.mav.send(message)

    response = connection.recv_match(type='COMMAND_ACK', blocking=True)
    if (response and response.command == mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED):
        print(f"Setting {WIND_COV_RATE_HZ = } Hz")
    else:
        print(f"Setting {WIND_COV_RATE_HZ = } failed")



def request_messages(connection, message_types: list) -> bool:
    for message_type in message_types:
        message = connection.mav.command_long_encode(
            connection.target_system,  # Target system ID
            connection.target_component,  # Target component ID
            mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,  # ID of command to send
            0,  # Confirmation
            message_type,  # param1: Message ID to be streamed
            0,       # param2 (unused)
            0,       # param3 (unused)
            0,       # param4 (unused)
            0,       # param5 (unused)
            0,       # param6 (unused)
            0        # param7: Response Target (0 - default, 1 - requestor, 2 - broadcast)
        )
        
        connection.mav.send(message)

        response = connection.recv_match(type='COMMAND_ACK', blocking=True)
        if (response and response.command == mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE and response.result == mavutil.mavlink.MAV_RESULT_ACCEPTED):
            print(f"Request for Message of type {message_type} ACCEPTED")
        else:
            print(f"Request for Message of type {message_type} DENIED")


def set_parameter(connection, param_id, param_value) -> bool:
    param_id = bytes(param_id, "ascii")
    # obtain parameter type
    connection.mav.param_request_read_send(
        connection.target_system,
        connection.target_component,
        param_id,
        -1
    )

    param_value_msg = connection.recv_match(type='PARAM_VALUE', blocking=True, timeout=3)
    print(param_value_msg)

    if param_value_msg is None:
        return False
    before = param_value_msg.param_value
    param_type = param_value_msg.param_type

    connection.mav.param_set_send(
        connection.target_system,
        connection.target_component,
        param_id,
        param_value,
        param_type
    )

    param_value_msg = connection.recv_match(type='PARAM_VALUE', blocking=True, timeout=3)
    print(param_value_msg)

    if param_value_msg is None:
        return False
    after = param_value_msg.param_value

    print(f"Value of parameter {param_id} changed from {before} to {after}")
    
    return before != after and after == param_value
