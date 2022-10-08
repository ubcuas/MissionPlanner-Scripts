from math import sqrt, pow
from conversion import convert_gps_to_utm

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

class Mission():
    def __init__(self):
        self._wplist = []
        self._index = 0
    
    def add_wp(self, wp):
        self._wplist.append(wp)
    
    def clear(self):
        self._wplist.clear()

    def mission_check_wp(self, current):
        #check distance to current wp
        if self._wplist[self._index].distance(current) <= 0.1:
            #update to next waypoint
            if (self._index < len(self._wplist) - 1):
                self._index += 1
            return True
        return False

    def mission_current_wp(self):
        return self._wplist[self._index]