from pymavlink import mavutil

def configure_camera(mav_connection: mavutil.mavfile, trigger_mode: str, trigger_time: int, trigger_dist: float) -> int:
    """
    trigger_mode: IMMEDIATE, INTERVAL, DIST
    trigger_time: if INTERVAL, the time between triggers
    trigger_dist: if DIST, distance between triggers
    """

    target_camera_id = 0 # TODO figure this out

    # TODO : figure out if sending TRIGG_INTERVAL after TRIGG_DIST or vice versa 
    # overwrites the previous configuration if it was a different type (e.g. sending
    # TRIGGER_DIST after TRIGG_INTERVAL will switch it from taking pictures based on 
    # time intervals to based on distance elapsed), or if the first one needs to be 
    # explicitly disabled

    if trigger_mode == "IMMEDIATE":
        mav_connection.mav.command_long_send(
            mav_connection.target_system,
            mav_connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_DIST,
            0, -1, 1, target_camera_id, 0, 0, 0
        )
    elif trigger_mode == "INTERVAL":
        mav_connection.mav.command_long_send(
            mav_connection.target_system,
            mav_connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_INTERVAL,
            trigger_time, -1, target_camera_id, 0, 0, 0, 0
        )
    elif trigger_mode == "DISTANCE":
        mav_connection.mav.command_long_send(
            mav_connection.target_system,
            mav_connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_CAM_TRIGG_DIST,
            int(trigger_dist), -1, 0, target_camera_id, 0, 0, 0
        )

    # Wait for the acknowledgment
    ack = mav_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1

    return ack.result

def trigger_camera(mav_connection: mavutil.mavfile, enable: int, reset: int = -1, pause: int = -1) -> int:

    target_camera_id = 0 # TODO figure this out

    mav_connection.mav.command_long_send(
        mav_connection.target_system,
        mav_connection.target_component, # TODO: probably different component than autopilot
        mavutil.mavlink.MAV_CMD_DO_TRIGGER_CONTROL,
        enable, reset, pause, target_camera_id, 0, 0, 0
    )

    # Wait for the acknowledgement
    ack = mav_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1

    return ack.result

# TODO: we may need to mess with gimbal managers/config, see https://mavlink.io/en/services/gimbal_v2.html
def retract_camera(mav_connection: mavutil.mavfile):

    mav_connection.mav.command_long_send(
        mav_connection.target_system,
        mav_connection.target_component, # TODO: probably different component than autopilot
        mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL,
        0, 0, 0, 0, 0, 0, 0 # 0 = Retract
    )

    # Wait for the acknowledgement
    ack = mav_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1
    
    return ack.result

def camera_location_point(mav_connection: mavutil.mavfile, lat: float, long: float, alt: float):

    mav_connection.mav.command_int_send(
        mav_connection.target_system,
        mav_connection.target_component, # TODO: probably different component than autopilot
        0, # MAV_FRAME
        mavutil.mavlink.MAV_CMD_DO_SET_ROI_LOCATION,
        0, 0,
        0, 0, 0, 0, int(lat * 10000000), int(long * 10000000), alt 
    )

    # Wait for the acknowledgement
    ack = mav_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1
    
    return ack.result

def camera_gimbal_pitchyaw(mav_connection: mavutil.mavfile, pitch: float, yaw: float, lock: bool):
    """
    if parameter `lock` is True, the gimbal's yaw will remain fixed and will not rotate with the vehicle.
    """
    
    mav_connection.mav.command_long_send(
        mav_connection.target_system,
        mav_connection.target_component, # TODO: probably different component than autopilot
        mavutil.mavlink.MAV_CMD_DO_GIMBAL_MANAGER_PITCHYAW,
        0, pitch, yaw, 
        0, 0, # pitch/yaw rate to 0
        16 if lock else 0,
        0, 0 # primary gimbal
    )

    # Wait for the acknowledgement
    ack = mav_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1
    
    return ack.result