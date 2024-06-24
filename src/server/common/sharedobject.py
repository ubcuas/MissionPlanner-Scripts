#from multiprocessing import Lock
from threading import Lock
from typing import Optional

from server.common.status import Status
from server.common.wpqueue import WaypointQueue

class SharedObject():
    def __init__(self):
        # Current mission fields
        self._currentmission = []
        self._currentmission_length = 0
        self._currentmission_flg_update = False
        self._currentmission_flg_ready = False
        self._currentmission_lk = Lock()

        # New mission fields
        self._newmission: WaypointQueue = []
        self._newmission_lk = Lock()
        self._newmission_flag: bool = False
        self._newmission_flag_lk = Lock()

        # New insertion fields
        self._newinsert: WaypointQueue = []
        self._newinsert_lk = Lock()
        self._newinsert_flag: bool = False
        self._newinsert_flag_lk = Lock()

        # Status fields
        self._status: Status = Status()
        self._status_lk = Lock()

        # Takeoff fields
        self._takeoffalt = 0
        self._takeoffalt_lk = Lock()
        self._takeoff_result_flag = False
        self._takeoff_result = 0

        # New home fields
        self._newhome = {}
        self._newhome_flag = False
        self._newhome_lk = Lock()

        # rtl and landing flags
        self._rtl_flag = False
        self._rtl_value = 0
        self._landing_flag = False
        self._rtl_land_lk = Lock()

        # vtol land flags
        self._vtol_land_flag = False 
        self._vtol_land_pos = {}
        self._vtol_land_lk = Lock()

        # vtol flags
        self._vtol_mode = 3 #start in VTOL
        self._vtol_lk = Lock()

        # voice flags
        self._voice_flag = False
        self._voice_text = ""
        self._voice_lk = Lock()

        # flightmode flags
        self._flightmode_flag = False
        self._flightmode = ""
        self._flightmode_lk = Lock()
        self._flightConfig = ""
        self._flightConfig_lk = Lock()

        # altitude standard flags
        self.altitude_standard = "AGL"
        self.altitude_standard_lk = Lock()

        # append_wp flags
        self._append_wp_flag = False
        self._append_wp_lk = Lock()
        self._append_wp = None

        # arm/disarm fields
        self._arm_flag = False
        self._arm_result_flag = False
        self._arm_lk = Lock()
        self._arm_status = 0
        self._arm_result = 0

    def arm_set(self, status):
        self._arm_lk.acquire()
        self._arm_flag = True
        self._arm_status = status
        self._arm_lk.release()
    
    def arm_get(self):
        if self._arm_flag:
            self._arm_lk.acquire()
            ret = self._arm_status
            self._arm_flag = False
            self._arm_lk.release()
            return ret
        else:
            return None
    
    def arm_set_result(self, result):
        self._arm_lk.acquire()
        self._arm_result_flag = True
        self._arm_result = result
        self._arm_lk.release()
    
    def arm_get_result(self):
        if self._arm_result_flag:
            self._arm_lk.acquire()
            ret = self._arm_result
            self._arm_result_flag = False
            self._arm_lk.release()
            return ret
        else:
            return None
    
    def append_wp_set(self, wp):
        self._append_wp_lk.acquire()
        self._append_wp_flag = True
        self._append_wp = wp
        self._append_wp_lk.release()
    
    def append_wp_get(self):
        if self._append_wp_flag:
            self._append_wp_lk.acquire()
            ret = self._append_wp
            self._append_wp_flag = False
            self._append_wp = None
            self._append_wp_lk.release()
            return ret
        else:
            return None
    
    # Currentmission methods
    def gcom_currentmission_get(self):
        ret = []
        self._currentmission_lk.acquire()
        ret = self._currentmission
        self._currentmission_lk.release()
        return ret
    
    def mps_currentmission_update(self, num):
        self._currentmission_lk.acquire()
        target = self._currentmission_length - num + 1
        while (len(self._currentmission) > target and len(self._currentmission) != 0):
            self._currentmission.pop(0)
            #print("SHAREDOBJ : popped", num, target)
        self._currentmission_lk.release()

    # newmission methods
    def gcom_newmission_flagcheck(self) -> bool:
        return self._newmission_flag
    
    def gcom_newmission_set(self, wpq: WaypointQueue) -> bool:
        self._newmission_flag_lk.acquire()
        self._newmission_flag = True
        
        self._newmission_lk.acquire()
        self._newmission = wpq
        
        self._newmission_lk.release()
        self._newmission_flag_lk.release()
    
        return True

    def mps_newmission_get(self) -> Optional[WaypointQueue]: 
        if self._newmission_flag:
            self._newmission_flag_lk.acquire()
            self._newmission_flag = False

            self._newmission_lk.acquire()
            ret = self._newmission
            self._newmission = []
            
            self._newmission_lk.release()
            self._newmission_flag_lk.release()

            self._currentmission_lk.acquire()
            self._currentmission = ret.aslist()
            self._currentmission_length = ret.size()
            self._currentmission_lk.release()

            return ret
        else:
            return None
    
    def gcom_newinsert_flagcheck(self) -> bool:
        return self._newinsert_flag

    def gcom_newinsert_set(self, wpq: WaypointQueue) -> bool:
        self._newinsert_flag_lk.acquire()
        self._newinsert_flag = True
        
        self._newinsert_lk.acquire()
        self._newinsert = wpq
        
        self._newinsert_lk.release()
        self._newinsert_flag_lk.release()

        return True

    def mps_newinsert_get(self) -> Optional[WaypointQueue]: 
        if self._newinsert_flag:
            self._newinsert_flag_lk.acquire()
            self._newinsert_flag = False

            self._newinsert_lk.acquire()
            ret = self._newinsert
            self._newinsert = []
            
            self._newinsert_lk.release()
            self._newinsert_flag_lk.release()

            return ret
        else:
            return None
    
    # Status methods
    def set_status(self, updated: Status) -> None:
        self._status_lk.acquire()
        self._status = updated 
        self._status_lk.release()

    def get_status(self) -> Status:
        ret = ()
        self._status_lk.acquire()
        ret = self._status 
        self._status_lk.release()
        return ret

    # takeoff methods
    def gcom_takeoffalt_set(self, alt):
        self._takeoffalt_lk.acquire()
        self._takeoffalt = alt
        self._takeoffalt_lk.release()
    
    def mps_takeoffalt_get(self):
        if (self._takeoffalt != 0):
            self._takeoffalt_lk.acquire()
            ret = self._takeoffalt
            self._takeoffalt = 0
            self._takeoffalt_lk.release()
            return ret
        else:
            return 0
        
    def takeoff_set_result(self, result):
        self._takeoffalt_lk.acquire()
        self._takeoff_result_flag = True
        self._takeoff_result = result
        self._takeoffalt_lk.release()
    
    def takeoff_get_result(self):
        if self._takeoff_result_flag:
            self._takeoffalt_lk.acquire()
            ret = self._takeoff_result
            self._takeoff_result_flag = False
            self._takeoffalt_lk.release()
            return ret
        else:
            return None
    
    # New home methods
    def gcom_newhome_set(self, wp):
        self._newhome_lk.acquire()
        self._newhome = wp
        self._newhome_flag = True
        self._newhome_lk.release()
    
    def mps_newhome_get(self):
        if self._newhome_flag:
            self._newhome_lk.acquire()
            ret = self._newhome
            self._newhome_flag = False
            self._newhome = None
            self._newhome_lk.release()
            return ret
        else:
            return None

    # rtl/landing methods
    def gcom_rtl_set(self, val):
        self._rtl_land_lk.acquire()
        self._rtl_flag = True
        self._rtl_value = val
        self._rtl_land_lk.release()
    
    def mps_rtl_get(self):
        if self._rtl_flag:
            self._rtl_land_lk.acquire()
            self._rtl_flag = False
            ret = self._rtl_value
            self._rtl_value = 0
            self._rtl_land_lk.release()
            return ret
        return None
    
    def gcom_landing_set(self, val):
        self._rtl_land_lk.acquire()
        self._landing_flag = val
        self._rtl_land_lk.release()
    
    def mps_landing_get(self):
        if self._landing_flag:
            self._landing_flag = False
            return True
        return False

    # vtol landing methods
    def gcom_vtol_land_set(self, pos):
        self._vtol_land_lk.acquire()
        self._vtol_land_pos = pos 
        self._vtol_land_flag = True 
        self._vtol_land_lk.release()
    
    def mps_vtol_land_get(self):
        if self._vtol_land_flag:
            self._vtol_land_lk.acquire()
            ret = self._vtol_land_pos
            self._vtol_land_flag = False
            self._vtol_land_pos = None
            self._vtol_land_lk.release()
            return ret
        else:
            return None
    
    # vtol methods
    def gcom_vtol_set(self, val):
        self._vtol_lk.acquire()
        self._vtol_mode = val
        self._vtol_flag = True
        self._vtol_lk.release()
    
    def mps_vtol_get(self):
        self._vtol_lk.acquire()
        ret = self._vtol_mode
        self._vtol_lk.release()
        return ret
    
    # flightmode methods
    def flightmode_set(self, mode):
        self._flightmode_lk.acquire()
        self._flightmode_flag = True
        self._flightmode = mode
        self._flightmode_lk.release()

    def flightmode_get(self):
        self._flightmode_lk.acquire()
        ret = self._flightmode
        self._flightmode = ""
        self._flightmode_flag = False
        self._flightmode_lk.release()
        return ret

    def flightConfig_set(self, config):
        self._flightConfig_lk.acquire()
        self._flightConfig = config
        self._flightConfig_lk.release()
    
    def flightConfig_get(self):
        self._flightConfig_lk.acquire()
        ret = self._flightConfig
        self._flightConfig = ""
        self._flightConfig_lk.release()
        return ret

    # altitude standard methods
    def altitude_standard_set(self, standard):
        self.altitude_standard_lk.acquire()
        self.altitude_standard = standard
        self.altitude_standard_lk.release()

    def altitude_standard_get(self):
        self.altitude_standard_lk.acquire()
        ret = self.altitude_standard
        self.altitude_standard = ""
        self.altitude_standard_lk.release()
        return ret
    
    #mps -> gcom queue
    def mps_currentmission_updatequeue(self, wplist):
        self._currentmission_lk.acquire()
        self._currentmission_flg_ready = True
        self._currentmission = wplist
        self._currentmission_lk.release()
    
    def mps_currentmission_shouldupdate(self):
        self._currentmission_lk.acquire()
        ret = self._currentmission_flg_update
        if ret:
            self._currentmission_flg_update = False
        self._currentmission_lk.release()
        return ret
    
    def gcom_currentmission_trigger_update(self):
        self._currentmission_lk.acquire()
        self._currentmission_flg_update = True
        self._currentmission_flg_ready = False
        self._currentmission_lk.release()