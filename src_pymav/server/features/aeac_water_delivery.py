from server.common.wpqueue import WaypointQueue, Waypoint

def generate_water_wps(current_alt, deliver_alt, deliver_duration_secs, curr_lat, curr_lon):

    landing_mission = WaypointQueue()

    wp_1 = Waypoint(
        "Start",
        "curr_wp",
        curr_lat,
        curr_lon,
        current_alt,
    )

    wp_2 = Waypoint(
        "stay",
        "curr_wp",
        curr_lat,
        curr_lon,
        deliver_alt,
        command="LOITER_TIME",
        p1=deliver_duration_secs
    )

    wp_3 = Waypoint(
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

