import threading

class ThreadVar:
    def __init__(self, init):
        self.val=init
        self.lock = threading.Lock()
    def setVal(self, v):
        self.lock.acquire()
        self.val=v
        self.lock.release()
    def getVal(self):
        retv=""
        self.lock.acquire()
        retv=self.val
        self.lock.release()
        return retv

