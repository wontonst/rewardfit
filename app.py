import sys
import thread
import time
from firebase import firebase
from plumbum import local
from plumbum.cmd import cp, echo
import SimpleHTTPServer
import SocketServer
from app_tcp_handler import AppTCPHandler
from app_constants import AppConstants
from app_threadvar import ThreadVar
import os.path

steps = ThreadVar(0)
resetHost = cp['/etc/hosts.backup', '/etc/hosts']
firebase = firebase.FirebaseApplication(
    'https://torrid-torch-8987.firebaseio.com/',
    None)

# Every hackathon I use a huge web framework yada yada yada. Well this
# time I'm going to write my own bare metal server.
SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(("", AppConstants.PORT), AppTCPHandler)

def runServer():
    print "Server starting on port", AppConstants.PORT
    httpd.serve_forever()

def pullFromServer():
    result = firebase.get('/',None)
    return result['steps']

def pullAndBlock():
    """Pulls steps and updates list of blocked sites"""
    raw = pullFromServer()
    block(raw)
    reloadCache()
    steps.setVal(raw)

def generateSite(site):
    """Generate site based on steps and URL being visited"""
    from jinja2 import Template
    template = Template(
        open('template.html', 'r').read()
        )
    return template.render(steps=steps.getVal(), site=site)

def block(steps):
    """Block websites based on number of steps and threshold"""
    for t in AppConstants.THRESHOLDS:
        if steps < t[1]:
            (echo["127.0.0.1 ",t[0]+".com"] >> "/etc/hosts")()
            (echo["127.0.0.1 ","www."+t[0]+".com"] >> "/etc/hosts")()

def reloadCache():
    (local["dscacheutil"]["-flushcache"])()

def updateLoop():
    while True:
        print "Updating fitness data"
        pullAndBlock()
        time.sleep(AppConstants.PULL_RATE)

def checkHostsFile():
    """Will check if hosts has been backed up and back it up if needed"""
    if not os.path.isfile("/etc/hosts.backup"):
        cp["/etc/hosts", "/etc/hosts.backup"]()

if __name__ == "__main__":
    try:
        checkHostsFile()
        thread.start_new_thread(updateLoop, ())
        time.sleep(.1)  # makes stdout cleaner
        runServer()
    except IOError as e:
        if e[0] == errno.EPERM:
            print "Require root permission to run!"
    except KeyboardInterrupt:
        print "Caught interrupt. Closing"
    except:
        print "Unexpected exception caught. Cleaning and closing."
        print sys.exc_info()[0],sys.exc_info()[1]
    finally:
        print "Closing"
        httpd.server_close()
