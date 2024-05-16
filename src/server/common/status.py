import struct

class Status():
    def __init__(self):
        self._timestamp: int = 0
        self._wpn: int = -1 #current waypoint number

        self._lat: float = 0
        self._lng: float = 0
        self._alt: float = 0

        self._rol: float = 0 #roll
        self._pch: float = 0 #pitch
        self._yaw: float = 0 #yaw

        self._asp: float = 0 #airspeed
        self._gsp: float = 0 #groundspeed

        self._btv: float = 0 #battery voltage
        
        self._wdr: float = 0 #wind direction
        self._wvl: float = 0 #wind velocity
    
    def encoded_status(self) -> bytes:
        return struct.pack('2i11f',
                           self._timestamp,
                           self._wpn,
                           self._lat,
                           self._lng,
                           self._alt,
                           self._rol,
                           self._pch,
                           self._yaw,
                           self._asp,
                           self._gsp,
                           self._btv,
                           self._wdr,
                           self._wvl)

    def decode_status(self, status_bytes: bytes) -> None:
        (self._timestamp, self._wpn, 
        self._lat, self._lng, self._alt, 
        self._rol, self._pch, self._yaw, 
        self._asp, self._gsp, 
        self._btv, 
        self._wdr, self._wvl) = struct.unpack('2i11f', status_bytes)

    def as_dictionary(self) -> dict:
        return {
            'timestamp'     : self._timestamp,
            'current_wpn'   : self._wpn,
            'latitude'      : self._lat,
            'longitude'     : self._lng,
            'altitude'      : self._alt,
            'roll'          : self._rol,
            'pitch'         : self._pch,
            'yaw'           : self._yaw,
            'airspeed'      : self._asp,
            'groundspeed'   : self._gsp,
            'batteryvoltage': self._btv,
            'winddirection' : self._wdr,
            'windvelocity'  : self._wvl,
        }