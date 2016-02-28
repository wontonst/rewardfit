import threading

class ThreadVar:
    def __init__(self, init):
        self.val=init
        self.lock = threading.Lock()

    def setVal(self, v):
        if v is None:
            raise BaseException
        print "Setting to {}".format(v)
        self.lock.acquire()
        self.val=v
        self.lock.release()

    def getVal(self):
        retv=""
        self.lock.acquire()
        retv=self.val
        self.lock.release()
        return retv

    def __str__(self):
        return str(self.getVal())
