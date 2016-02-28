import os.path
import sys
import thread
import time
from plumbum.cmd import cp
from app_constants import AppConstants
from rewardfit import RewardFit
from app_server import AppServer
from fitbit import FitBit

def checkHostsFile():
    """Will check if hosts has been backed up and back it up if needed"""
    if not os.path.isfile("/etc/hosts.backup"):
        cp["/etc/hosts", "/etc/hosts.backup"]()

if __name__ == "__main__":
    server = AppServer()
    try:
        checkHostsFile()
        FitBit.tryLogin()
        rf = RewardFit(server=server)
        thread.start_new_thread(rf.updateLoop, ())
        time.sleep(.1)  # makes stdout cleaner
        server.runServer()
    except IOError as e:
        if e[0] == errno.EPERM:
            print "Require root permission to run!"
    except KeyboardInterrupt:
        print "Caught interrupt. Closing"
    finally:
        print "Closing"
        server.killServer()
