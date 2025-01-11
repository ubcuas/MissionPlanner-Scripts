import math
from matplotlib import pyplot as plt

from server.common.conversion import *
from server.common.wpqueue import Waypoint, WaypointQueue

# ALL UNITS IN METERS UNLESS SPECIFIED
SPLINE_WAYPOINT_TYPE = "SPLINE_WAYPOINT"
TURNING_RADIUS = 20
EARTH_RADIUS = 6378 * 1000 # 6378 km

def calculate_scan_radius(altitude, vertical_fov_deg, horizontal_fov_deg) -> int:
    # Convert FOV angles from degrees to radians
    h_fov_rad = math.radians(vertical_fov_deg)
    v_fov_rad = math.radians(horizontal_fov_deg)

    # Calculate the width and height of the scanned area at given altitude
    width = 2 * altitude * math.tan(h_fov_rad / 2)  # Horizontal dimension
    height = 2 * altitude * math.tan(v_fov_rad / 2)  # Vertical dimension

    return min(width, height) // 2 # in meters


def plot_shape(points, color, close_loop=False, scatter=True) -> None:
    adjust = 0 if close_loop else 1

    #plot points
    if scatter:
        plt.scatter([pt[0] for pt in points], [pt[1] for pt in points], color=color)

    
    for i, pt in enumerate(points):
        plt.text(pt[0], pt[1], str(i), fontsize=8, color='red', ha='right')

    #plot connecting lines
    for i in range(len(points) - adjust):
        curr = points[i]
        next = points[(i + 1) % len(points)]
        plt.plot([curr[0], next[0]], [curr[1], next[1]], color=color, alpha=0.7, linewidth=1, zorder=2)

def scan_area(center_lat, center_lng, altitude, target_area_radius) -> WaypointQueue:
    wpq = WaypointQueue()
    center_we, center_sn = convert_gps_to_utm(center_lat, center_lng)
    zone = convert_gps_to_utm_zone(center_lng)
    hemisphere = 1 # +1 for North, -1 for South
    # wpq = []
    record = []
    count = 0

    scan_radius = calculate_scan_radius(altitude, 44, 57) # from v1226-mpz 20MP Lens (12 mm focal)
    print(scan_radius)
    
    # go to center waypoint (with generous slack)
    wpq.push(Waypoint(0, "", center_lat, center_lng, altitude, command=SPLINE_WAYPOINT_TYPE))
    count += 1
    record.append((center_we, center_sn))
    # # wpq.append((0, "", center_lat, center_lng, altitude))

    # transit from center to edge, turning gently so that drone is tangent when reaching the edge
    tmp_lat, tmp_lng = convert_utm_to_gps(center_we + target_area_radius / 2, center_sn - target_area_radius / 2, zone, hemisphere)
    record.append((center_we + target_area_radius / 2, center_sn - target_area_radius / 2))
    wpq.push(Waypoint(count, "", tmp_lat, tmp_lng, altitude))
    count += 1

    tmp_lat, tmp_lng = convert_utm_to_gps(center_we + target_area_radius, center_sn, zone, hemisphere)
    record.append((center_we + target_area_radius, center_sn))
    wpq.push(Waypoint(count, "", tmp_lat, tmp_lng, altitude))
    count += 1
    
    # generate spiral
    decrease_per_radian = 0.75 * (scan_radius) / (2 * math.pi)
    current_angle = 0
    current_radius = target_area_radius
    THRESHOLD = scan_radius

    while current_radius >= TURNING_RADIUS:
        delta_rad = THRESHOLD / current_radius

        current_angle += delta_rad
        if current_angle > 2 * math.pi:
            current_angle -= 2 * math.pi

        current_radius -= decrease_per_radian * delta_rad
        #print(f"{delta_rad = }; {current_angle = }; {current_radius = }")

        # place waypoint
        record.append((center_we + current_radius * math.cos(current_angle), center_sn + current_radius * math.sin(current_angle)))
        tmp_lat, tmp_lng = convert_utm_to_gps(center_we + current_radius * math.cos(current_angle), center_sn + current_radius * math.sin(current_angle), zone, hemisphere)
        wpq.push(Waypoint(count, "", tmp_lat, tmp_lng, altitude, command=SPLINE_WAYPOINT_TYPE, p2=2))
        count += 1
    
    # plot_shape(record, color="green", close_loop=False, scatter=True)
    # plot_shape([(wp._lng, wp._lat) for wp in wpq.aslist()], color="blue", close_loop=False, scatter=True)
    # plt.grid()
    # ax = plt.gca()
    # ax.set_aspect('equal', adjustable='box')
    # plt.show()

    return wpq
    
    # TODO handle deadzone

if __name__ == '__main__':
    scan_area(0,0,100, 100)