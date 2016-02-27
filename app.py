import thread
import threading
import time
from firebase import firebase
from plumbum import local
from plumbum.cmd import cp, echo
import SimpleHTTPServer
import SocketServer

resetHost = cp['/etc/hosts.backup', '/etc/hosts']
PULL_RATE=3
PORT = 8000
firebase = firebase.FirebaseApplication(
    'https://torrid-torch-8987.firebaseio.com/',
    None)

response="UNSET!"
lock = threading.Lock()

class AppTCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        self.wfile.write(response)

SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(("", PORT), AppTCPHandler)



def setResponse(nv):
    global response
    lock.acquire()
    response=nv
    lock.release()
def getResponse():
    retval = "bad"
    lock.acquire()
    retval=response
    lock.release()
    return retval

def runServer():
    print "serving at port", PORT
    httpd.serve_forever()

def pullFromServer():
    result = firebase.get('/',None)
    return result['steps']

def pullBlockGenerate():
    raw = pullFromServer()
    block(raw)
    reloadCache()
    return generateSite(raw)

def generateSite(raw):
    from jinja2 import Template
    template = Template(
        open('template.html', 'r').read()
        )
    return template.render(steps=raw)

def block(steps):
    thresholds = [
        ('netflix', 10000),
        ('facebook', 5000),
        ('reddit', 2500),
        ('twitter', 1000)
        ]
    for t in thresholds:
        if steps < t[1]:
            print t
            (echo["127.0.0.1 ",t[0]+".com"] >> "/etc/hosts")()
            (echo["127.0.0.1 ","www."+t[0]+".com"] >> "/etc/hosts")()

def reloadCache():
    (local["dscacheutil"]["-flushcache"])()

def updateLoop():
    while True:
        print "loop"
        setResponse(pullBlockGenerate())
        print response
        time.sleep(PULL_RATE)

if __name__ == "__main__":
    try:
        thread.start_new_thread(updateLoop, ())
        runServer()
    except:
        print "Exception caught. Cleaning and closing"
        httpd.server_close()
