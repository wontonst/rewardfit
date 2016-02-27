import thread
import threading
import time
from firebase import firebase
from plumbum import local
from plumbum.cmd import cp, echo
import SimpleHTTPServer
import SocketServer

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

steps=ThreadVar(0)

THRESHOLDS = [
    ('netflix', 10000),
    ('facebook', 5000),
    ('reddit', 2500),
    ('twitter', 1000)
]

resetHost = cp['/etc/hosts.backup', '/etc/hosts']
PULL_RATE=3
PORT = 80
firebase = firebase.FirebaseApplication(
    'https://torrid-torch-8987.firebaseio.com/',
    None)

class AppTCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        trysite=None
        self.data = self.request.recv(1024).strip()
        for t in THRESHOLDS:
            if t[0] in self.data:
                trysite = t
                break
        self.wfile.write(generateSite(trysite))

SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(("", PORT), AppTCPHandler)

def runServer():
    print "serving at port", PORT
    httpd.serve_forever()

def pullFromServer():
    result = firebase.get('/',None)
    return result['steps']

def pullAndBlock():
    raw = pullFromServer()
    block(raw)
    reloadCache()
    steps.setVal(raw)

def generateSite(site):
    from jinja2 import Template
    template = Template(
        open('template.html', 'r').read()
        )
    return template.render(steps=steps.getVal(), site=site)

def block(steps):
    for t in THRESHOLDS:
        if steps < t[1]:
            (echo["127.0.0.1 ",t[0]+".com"] >> "/etc/hosts")()
            (echo["127.0.0.1 ","www."+t[0]+".com"] >> "/etc/hosts")()

def reloadCache():
    (local["dscacheutil"]["-flushcache"])()

def updateLoop():
    while True:
        print "updateLoop"
        pullAndBlock()
        time.sleep(PULL_RATE)

if __name__ == "__main__":
    try:
        thread.start_new_thread(updateLoop, ())
        runServer()
    except:
        print "Exception caught. Cleaning and closing"
        httpd.server_close()
