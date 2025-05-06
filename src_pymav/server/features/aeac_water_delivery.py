from server.common.wpqueue import WaypointQueue, Waypoint
from server.common.callback import CallbackSystem, Callback
from server.operations.rc_channel_cmd import send_rc_channel_value
from pymavlink import mavutil


AEAC_PUMP_CHANNEL = 7

'''
Generates a water delivery mission with the following waypoints:
1. Start at current location
2. Loiter down to delivery altitude for a specified duration (deliver_duration_secs)
3. Send signal to deliver water
3. Return to previous location altitude
'''
def generate_water_wps(
    current_alt: float,
    deliver_alt: float,
    deliver_duration_secs: int,
    curr_lat: float,
    curr_lon: float,
) -> tuple[WaypointQueue, list[Callback]]:
    landing_mission = WaypointQueue()
    callbacks = []

    # Set the current altitude to the current location
    wp_1 = Waypoint(
        "Start",
        "curr_wp",
        curr_lat,
        curr_lon,
        current_alt,
    )

    wp_2 = Waypoint(
        "pre-loiter",
        "curr_wp",
        curr_lat,
        curr_lon,
        deliver_alt,
    )

    # Add a callback to set the payload mode to release water after getting to loiter wp 
    callbacks.append(Callback(
        "Water Delivery - Release water",
        'MISSION_CURRENT',
        lambda curr_msg, prev_msg: (curr_msg.seq == 3),
        lambda msg, conn, state: set_payload_mode(
            mav_connection=conn,
            valve_one_open=False,
            valve_two_open=True,
            pump_on=False,
            reset=False
        ),
        removable_flags = {
            "on_payload_fired": True,
            "on_mission_switched": True,
        }
    ))

    wp_3 = Waypoint(
        "stay",
        "curr_wp",
        curr_lat,
        curr_lon,
        deliver_alt,
        command="LOITER_TIME",
        p1=deliver_duration_secs,
    )
    

    wp_4 = Waypoint(
        "post-loiter",
        "curr_wp",
        curr_lat,
        curr_lon,
        deliver_alt,
    )

    # Add a callback to set the payload mode to stop releasing water after getting to loiter wp 
    callbacks.append(Callback(
        "Water Delivery - Stop releasing water",
        'MISSION_CURRENT',
        lambda curr_msg, prev_msg: (curr_msg.seq == 5),
        lambda msg, conn, state: set_payload_mode(
            mav_connection=conn,
            valve_one_open=False,
            valve_two_open=False,
            pump_on=False,
            reset=False
        ),
        removable_flags = {
            "on_payload_fired": True,
            "on_mission_switched": True,
        }
    ))

    wp_5 = Waypoint(
        "Return",
        "curr_wp",
        curr_lat,
        curr_lon,
        current_alt,
        command="LOITER_UNLIM",
    )

    landing_mission.push(wp_1)
    landing_mission.push(wp_2)
    landing_mission.push(wp_3)
    landing_mission.push(wp_4)
    landing_mission.push(wp_5)

    return landing_mission, callbacks

def set_payload_mode(mav_connection: mavutil.mavfile, valve_one_open: bool, 
                     valve_two_open: bool, pump_on: bool, reset: bool = False) -> int:

    # Two switches are used on the payload
    # SWITCH 1 represents the state of valve one and valve two
    # Three possible states:
    # 1. UP   (100) - Valve one open and valve two closed
    # 2. MID  (300) - Both valves closed
    # 3. DOWN (500) - Valve one closed and valve two open

    # SWITCH 2 represents the state of the pump
    # Two possible states:
    # 1. ON   (1)   - Pump on
    # 2. OFF  (-1)  - Pump off

    # value = 1500 + SWITCH 1 * SWITCH 2 

    print(f"Setting payload mode with valve_one_open: {valve_one_open}, "
          f"valve_two_open: {valve_two_open}, pump_on: {pump_on}")

    if reset:
        print("PAYLOAD: Resetting channel back to pilot control")
        value = 0
    if pump_on and valve_one_open and not valve_two_open:
        print("PAYLOAD: Set to intake water")
        value = 1500 + 100 * 1
    elif not pump_on and not valve_one_open and not valve_two_open:
        print("PAYLOAD: Set to transport water")
        value = 1500 + 300 * -1
    elif not pump_on and not valve_one_open and valve_two_open:
        print("PAYLOAD: Set to release water")
        value = 1500 + 500 * -1
    elif not pump_on and valve_one_open and valve_two_open:
        print("PAYLOAD: Set to refill reservoir")
        value = 1500 + 100 * -1
    else:
        print("Invalid combination of valve and pump states.")
        return -1
    
    result = send_rc_channel_value(mav_connection=mav_connection, channel=AEAC_PUMP_CHANNEL, value=value)

    if result == -1:
        print(f"Failed to set payload value to {value}")
    else:
        print(f"Sucessfully set payload value to {value}")