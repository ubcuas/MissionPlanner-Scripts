import struct

class Status():
    def __init__(self, timestamp = 0, waypoint_number = -1, 
                 latitude = 0, longitude = 0, altitude = 0,
                 roll = 0, pitch = 0, yaw = 0, 
                 airspeed = 0, groundspeed = 0, verticalspeed = 0,
                 battery_voltage = 0, 
                 wind_direction = 0, wind_velocity = 0):
        
        self._timestamp: int = timestamp
        self._wpn: int = waypoint_number

        self._lat: float = latitude
        self._lng: float = longitude
        self._alt: float = altitude

        self._rol: float = roll
        self._pch: float = pitch
        self._yaw: float = yaw

        self._asp: float = airspeed
        self._gsp: float = groundspeed
        self._vsp: float = verticalspeed

        self._btv: float = battery_voltage
        
        self._wdr: float = wind_direction
        self._wvl: float = wind_velocity
    
    def encoded_status(self) -> bytes:
        return struct.pack('Qi12f',
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
                           self._vsp,
                           self._btv,
                           self._wdr,
                           self._wvl)

    def decode_status(self, status_bytes: bytes) -> None:
        (self._timestamp, self._wpn, 
        self._lat, self._lng, self._alt, 
        self._rol, self._pch, self._yaw, 
        self._asp, self._gsp, self._vsp,
        self._btv, 
        self._wdr, self._wvl) = struct.unpack('Qi12f', status_bytes)

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
            'verticalspeed' : self._vsp,
            'batteryvoltage': self._btv,
            'winddirection' : self._wdr,
            'windvelocity'  : self._wvl,
        }
    
    def as_reduced_status(self) -> dict:
        return {
            'timestamp' : self._timestamp,
            'latitude' : self._lat,
            'longitude' : self._lng,
            'altitude' : self._alt,
            'vertical_velocity': self._vsp,
            'velocity': self._gsp,
            'heading': self._yaw,
            'battery_voltage' : self._btv
        }
    