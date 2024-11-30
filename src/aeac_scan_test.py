import math
from matplotlib import pyplot as plt

# from server.common.conversion import *
# from server.common.wpqueue import Waypoint, WaypointQueue

# ALL UNITS IN METERS UNLESS SPECIFIED

TURNING_RADIUS = 20
EARTH_RADIUS = 6378 * 1000 # 6378 km

def calculate_scan_radius(altitude, vertical_fov_deg, horizontal_fov_deg):
    # Convert FOV angles from degrees to radians
    h_fov_rad = math.radians(vertical_fov_deg)
    v_fov_rad = math.radians(horizontal_fov_deg)

    # Calculate the width and height of the scanned area at given altitude
    width = 2 * altitude * math.tan(h_fov_rad / 2)  # Horizontal dimension
    height = 2 * altitude * math.tan(v_fov_rad / 2)  # Vertical dimension

    return min(width, height) // 2 # in meters


def plot_shape(points, color, close_loop=False, scatter=True):
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

def scan_area(center_lat, center_lng, altitude, target_area_radius):
    # wpq = WaypointQueue()
    wpq = []

    scan_radius = calculate_scan_radius(altitude, 44, 57) # from v1226-mpz 20MP Lens (12 mm focal)
    print(scan_radius)
    
    # go to center waypoint (with generous slack)
    # wpq.push(Waypoint(0, "", center_lat, center_lng, altitude))
    wpq.append((0, "", center_lat, center_lng, altitude))

    # transit from center to edge, turning gently so that drone is tangent when reaching the edge
    
    # generate concentric circle
    shift_amount = math.pi / 8
    dist_from_center = target_area_radius

    while dist_from_center > TURNING_RADIUS:
        print(dist_from_center, scan_radius)
        curr_deg = 0

        while curr_deg <= 2 * math.pi:
            # Adjust center_lat and center_lng from degrees to radians
            center_lat_rad = math.radians(center_lat)
            center_lng_rad = math.radians(center_lng)

            # Calculate latitude and longitude
            new_latitude = center_lat + (180 / math.pi) * (dist_from_center / EARTH_RADIUS) * math.sin(curr_deg)
            new_longitude = center_lng + (180 / math.pi) * (dist_from_center / EARTH_RADIUS) / math.cos(center_lat_rad) * math.cos(curr_deg)


            # on first waypoint of queue do 
            wpq.append((0, "", new_latitude, new_longitude))
            curr_deg += shift_amount

        dist_from_center -= (scan_radius // 2)
    
    

    plot_shape([(wp[3], wp[2]) for wp in wpq], color="blue", close_loop=True, scatter=True)
    plt.show()


    # handle deadzone


scan_area(0,0,100, 100)