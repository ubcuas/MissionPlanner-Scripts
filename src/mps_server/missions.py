from math import sqrt, pow

from ..common.wpqueue import WaypointQueue, Waypoint

class Mission():
    def __init__(self, wpq=WaypointQueue()):
        self._wpq = wpq
        self._index = 0
        self._done = False
    
    def add_wp(self, wp):
        self._wplist.append(wp)
    
    def clear(self):
        self._wplist.clear()

    def mission_check_wp(self, current):
        #check distance to current wp
        if self._wplist[self._index].distance(current) <= 0.1:
            #update to next waypoint
            if (self._index == len(self._wplist) - 1):
                self._done = True
            else:
                self._index += 1
            return True
        return False

    def mission_complete(self):
        return self._done

    def mission_current_wp(self):
        return self._wplist[self._index]