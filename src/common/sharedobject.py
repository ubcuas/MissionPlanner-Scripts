import copy
from threading import Lock

from src.common.wpqueue import WaypointQueue

class SharedObject():
    def __init__(self):
        #current mission fields
        self._currentmission = []
        self._currentmission_lk = Lock()

        #new mission fields
        self._newmission = []
        self._newmission_lk = Lock()
        self._newmission_flag = False
        self._newmission_flag_lk = Lock()

        #status fields
        self._status = ()
        self._status_lk = Lock()

        #lock fields
        self._locked = False 
        self._locked_lk = Lock()
    
    #currentmission methods
    def gcom_currentmission_get(self):
        ret = []
        self._currentmission_lk.acquire()
        ret = self._currentmission
        self._currentmission_lk.release()
        return ret

    #newmission methods
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
            self._currentmission_lk.release()

            return ret
        else:
            return None
    
    #status methods
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

    #lock methods
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