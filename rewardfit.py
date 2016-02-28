from plumbum import local
from plumbum.cmd import echo, cp
import time
from firebase import firebase
from fitbit import FitBit
from app_constants import AppConstants

class RewardFit:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)

    def pullAndBlock(self):
        """Pulls steps and updates list of blocked sites"""
        FitBit.pullFromServer()
        self.block()
        
    def block(self):
        """Block websites based on number of steps and threshold"""
        # Reset hosts file
        cp['/etc/hosts.backup', '/etc/hosts']()
        for t in AppConstants.THRESHOLDS:
            if FitBit.steps.getVal() < t[1]:
                (echo["127.0.0.1 ",t[0]+".com"] >> "/etc/hosts")()
                (echo["127.0.0.1 ","www."+t[0]+".com"] >> "/etc/hosts")()
        self.reloadCache()

    def reloadCache(self):
        (local["dscacheutil"]["-flushcache"])()

    def updateLoop(self):
        while True:
            print "Updating fitness data"
            self.pullAndBlock()
            time.sleep(AppConstants.PULL_RATE)
