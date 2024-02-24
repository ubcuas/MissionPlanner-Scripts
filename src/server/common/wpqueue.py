from math import sqrt, pow

from server.common.conversion import convert_gps_to_utm

class Waypoint():
    def __init__(self, id, name, lat, lng, alt):
        self._id = id
        self._name = name
        self._lat = float(lat)
        self._lng = float(lng)
        self._alt = float(alt)

    def __str__(self):
        return f"{self._name} {self._lat} {self._lng} {self._alt}"
    
    def get_coords_gps(self):
        return (self._lat, self._lng, self._alt)
    
    def get_asdict(self):
        return {'id':self._id, 'name':self._name, 'latitude':self._lat, 'longitude':self._lng, 'altitude':self._alt}
    
    def get_coords_utm(self):
        this_utm = convert_gps_to_utm(self._lat, self._lng)
        return (this_utm[0], this_utm[1], self._alt)

    def distance(self, other_wp, altitude=True):
        this_utm = self.get_coords_utm()
        other_utm = other_wp.get_coords_utm()

        if altitude:
            altdist = pow(other_utm[2] - this_utm[2], 2)
        else:
            altdist = 0

        return sqrt(pow(other_utm[0] - this_utm[0], 2) + pow(other_utm[1] - this_utm[1], 2) + altdist)

class Queue():
    def __init__(self, inlist=[]):
        self._list = inlist.copy()
    
    def __str__(self):
        ret = ""
        for i in range(0, len(self._list)):
            ret += f"{i} : {str(self._list[i])}\n"
        return ret
    
    def clear(self):
        self._list = []
    
    def front(self):
        return self._list[0]

    def back(self):
        return self._list[-1]

    def empty(self):
        return (len(self._list) == 0)
    
    def size(self):
        return len(self._list)
    
    def push(self, wp):
        self._list.append(wp)

    def pop(self):
        return self._list.pop(0)

class WaypointQueue(Queue):
    def aslist(self):
        return self._list.copy()

if __name__ == "__main__":
    testq = Queue()

    assert(testq.size() == 0)
    assert(testq.empty())

    for i in range(0, 5):
        testq.push(i)
        assert(testq.back() == i)

    assert(testq.size() == 5)
    assert(not testq.empty())
    
    for i in range(0, 5):
        assert(testq.front() == i)
        x = testq.pop()
        assert(x == i)
    
    assert(testq.size() == 0)
    assert(testq.empty())

    lis2 = []

    for i in range(10, 0, -1):
        lis2.append(i)
    
    testq2 = Queue(lis2)

    assert(testq2.size() == 10)
    assert(testq2.front() == 10)
    assert(testq2.back() == 1)

    testq2.clear()

    assert(testq2.size() == 0)
    assert(testq2.empty())

    print("All tests passed")
    