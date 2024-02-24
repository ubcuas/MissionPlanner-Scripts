import threading

class CustomThread(threading.Thread):
    def __init__(self, target=None, args=(), kwargs={}):
        super(CustomThread, self).__init__(target=target, args=args, kwargs=kwargs)
        self._stopper = threading.Event()
    
    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def run(self):
        if self._target:
            self._target(*self._args, **self._kwargs)