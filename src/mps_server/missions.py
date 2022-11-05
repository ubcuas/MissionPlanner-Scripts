from src.common.wpqueue import WaypointQueue

class Mission():
    def __init__(self, wpq=WaypointQueue()):
        self._wpq = wpq
    
    def add_wp(self, wp):
        self._wpq.push(wp)
    
    def clear(self):
        self._wpq.clear()

    def mission_check_wp(self, current):
        #return true if no current wp
        if self._wpq.empty():
            return True
        
        #check distance to current wp
        if self._wpq.front().distance(current) <= 0.1:
            #update to next waypoint
            self._wpq.pop()
            return True
        return False

    def mission_complete(self):
        return self._wpq.empty()

    def mission_current_wp(self):
        return self._wpq.front()
    
    def mission_number_wps(self):
        return self._wpq.size()