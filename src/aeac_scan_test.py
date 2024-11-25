import math
from matplotlib import pyplot as plt

from server.common.conversion import *
from server.common.wpqueue import Waypoint, WaypointQueue

TURNING_RADIUS = 20

def calculate_scan_radius(altitude, vertical_fov_deg, horizontal_fov_deg):
    # Convert FOV angles from degrees to radians
    h_fov_rad = math.radians(vertical_fov_deg)
    v_fov_rad = math.radians(horizontal_fov_deg)

    # Calculate the width and height of the scanned area at given altitude
    width = 2 * altitude * math.tan(h_fov_rad / 2)  # Horizontal dimension
    height = 2 * altitude * math.tan(v_fov_rad / 2)  # Vertical dimension

    return min(width, height) // 2


def plot_shape(points, color, close_loop=False, scatter=True):
    adjust = 0 if close_loop else 1

    #plot points
    if scatter:
        plt.scatter([pt[0] for pt in points], [pt[1] for pt in points], color=color)

    #plot connecting lines
    for i in range(len(points) - adjust):
        curr = points[i]
        next = points[(i + 1) % len(points)]
        plt.plot([curr[0], next[0]], [curr[1], next[1]], color=color, alpha=0.7, linewidth=1, zorder=2)

def scan_area(center_lat, center_lng, altitude, target_area_radius) -> WaypointQueue:
    wpq = WaypointQueue()

    scan_radius = calculate_scan_radius(altitude, 44, 57) # from v1226-mpz 20MP Lens (12 mm focal)
    
    # go to center waypoint (with generous slack)
    wpq.push(Waypoint(0, "", center_lat, center_lng, altitude))

    # transit from center to edge, turning gently so that drone is tangent when reaching the edge
    


    # spiral inwards till deadzone

    # handle deadzone

