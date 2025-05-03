from pymavlink.mavutil import mavfile, mavlink


"""

cam_id: 0 is all cameras, 1 is camera 1, 2 is camera 2
num_of_pics: 0 is unlimited pictures, else limit to num_of_pics
"""

def activate_camera(mav_connection: mavfile, cam_id: int = 0, time_between_pics_secs: float = 1.0, num_of_pics: int = 0,
                    timeout: int = 5, tgt_sys_id: int = 1, tgt_comp_id: int = 1) -> int:
    
    mav_connection.mav.command_long_send(
        tgt_sys_id,
        tgt_comp_id,
        mavfile.mavlink.MAV_CMD_IMAGE_START_CAPTURE,
        cam_id, time_between_pics_secs, num_of_pics
    )

    # Wait for the acknowledgment
    ack = mav_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1

    print(f"ACTIVATE camera ack: {ack}")

    return ack.result

def deactivate_camera(mav_connection: mavfile, tgt_sys_id: int = 1, tgt_comp_id: int = 1, 
                    cam_id: int = 0, timeout: int = 5) -> int:
    
    mav_connection.mav.command_long_send(
        tgt_sys_id,
        tgt_comp_id,
        mavfile.mavlink.MAV_CMD_IMAGE_STOP_CAPTURE,
        cam_id
    )

    # Wait for the acknowledgment
    ack = mav_connection.recv_match(type='COMMAND_ACK', blocking=True, timeout=timeout)
    if ack is None:
        print('No acknowledgment received within the timeout period.')
        return -1

    print(f"DEACTIVATE camera ack: {ack}")

    return ack.result