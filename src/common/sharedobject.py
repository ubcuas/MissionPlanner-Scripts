from threading import Lock

from wpqueue import WaypointQueue

class SharedObject():
    def __init__(self):
        self._newmission = WaypointQueue()
        self._newmission_lk = Lock()
        self._newmission_flag = False
        self._newmission_flag_lk = Lock()
    
    def gcom_newmission_flagcheck(self):
        return self._newmission_flag
    
    def gcom_newmission_set(self, wpq):
        if self._newmission == True:
            return False
        
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
            self._newmission = WaypointQueue() #TODO check mutability
            
            self._newmission_lk.release()
            self._newmission_flag_lk.release()
            return ret
        else:
            return None