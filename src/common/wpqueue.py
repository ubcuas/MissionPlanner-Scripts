from math import sqrt, pow

from src.common.conversion import convert_gps_to_utm

class Waypoint():
    def __init__(self, lat, lng, alt):
        self._lat = float(lat)
        self._lng = float(lng)
        self._alt = float(alt)

    def __str__(self):
        return f"{self._lat} {self._lng} {self._alt}"
    
    def get_coords_gps(self):
        return (self._lat, self._lng, self._alt)
    
    def get_coords_utm(self):
        this_utm = convert_gps_to_utm(self._lat, self._lng)
        return (this_utm[0], this_utm[1], self._alt)

    def distance(self, other_wp):
        this_utm = self.get_coords_utm()
        other_utm = other_wp.get_coords_utm()

        return sqrt(pow(other_utm[0] - this_utm[0], 2) + pow(other_utm[1] - this_utm[1], 2) + pow(other_utm[2] - this_utm[2], 2))

class WaypointQueue():
    def __init__(self, wplist=[]):
        self._wplist = wplist
    
    def __str__(self):
        ret = ""
        for i in range(0, len(self._wplist)):
            ret += f"{i} : {str(self._wplist[i])}\n"
        return ret
    
    def clear(self):
        self._wplist = []
    
    def front(self):
        return self._wplist[0]

    def back(self):
        return self._wplist[-1]

    def empty(self):
        return (len(self._wplist) == 0)
    
    def size(self):
        return len(self._wplist)
    
    def push(self, wp):
        self._wplist.append(wp)

    def pop(self):
        return self._wplist.pop(0)
