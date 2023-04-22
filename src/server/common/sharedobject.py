from threading import Lock

class SharedObject():
    def __init__(self):
        # Current mission fields
        self._currentmission = []
        self._currentmission_length = 0
        self._currentmission_lk = Lock()

        # New mission fields
        self._newmission = []
        self._newmission_lk = Lock()
        self._newmission_flag = False
        self._newmission_flag_lk = Lock()

        # Status fields
        self._status = ()
        self._status_lk = Lock()

        # Lock fields
        self._locked = False 
        self._locked_lk = Lock()

        # Takeoff fields
        self._takeoffalt = 0
        self._takeoffalt_lk = Lock()

        # New home fields
        self._newhome = {}
        self._newhome_flag = False
        self._newhome_lk = Lock()

        # rtl and landing flags
        self._rtl_flag = False
        self._landing_flag = False
        self._rtl_land_lk = Lock()

        # vtol land flags
        self._vtol_land_flag = False 
        self._vtol_land_pos = {}
        self._vtol_land_lk = Lock()

        # vtol flags
        self._vtol_mode = 3 #start in VTOL
        self._vtol_lk = Lock()

    
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
    def gcom_newmission_flagcheck(self):
        return self._newmission_flag
    
    def gcom_newmission_set(self, wpq):
        self._newmission_flag_lk.acquire()
        self._newmission_flag = True
        
        self._newmission_lk.acquire()
        self._newmission = wpq
        
        self._newmission_lk.release()
        self._newmission_flag_lk.release()
    
        return True

    def mps_newmission_get(self): 
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
    
    # Status methods
    def mps_status_set(self, updated):
        self._status_lk.acquire()
        self._status = updated 
        self._status_lk.release()

    def gcom_status_get(self):
        ret = ()
        self._status_lk.acquire()
        ret = self._status 
        self._status_lk.release()
        return ret

    # Lock methods
    def gcom_locked_set(self, locked):
        ret = True
        self._locked_lk.acquire()
        if self._locked == locked:
            ret = False
        self._locked = locked 
        self._locked_lk.release()
        return ret
    
    def mps_locked_get(self):
        ret = True 
        self._locked_lk.acquire()
        ret = self._locked 
        self._locked_lk.release()
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
        self._rtl_flag = val
        self._rtl_land_lk.release()
    
    def mps_rtl_get(self):
        if self._rtl_flag:
            self._rtl_flag = False
            return True
        return False
    
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
