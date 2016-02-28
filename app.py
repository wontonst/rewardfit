import thread
import threading
import base64
import time
import requests
import json
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

steps = ThreadVar(0)

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
fitbit=json.loads(open('auth.json','r').read())

# Every hackathon I use a huge web framework yada yada yada. Well this
# time I'm going to write my own bare metal server.

class AppTCPHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        trysite=None
        self.data = self.request.recv(2048)
        print self.data
        if "GET /fitbit?code=" in self.data:
            print "----HANDLING FITBIT OAUTH REQUEST----"
            code = self.data[self.data.find("code")+5:self.data.find("HTTP")-1]
            payload={"grant_type":"authorization_code",
                                "client_id":fitbit['client_id'],
                     "redirect_uri":"http://localhost/fitbit",
                     "code":code}
            authraw="{}:{}".format(fitbit['client_id'],fitbit['client_secret'])
            b64auth="Basic "+base64.b64encode(authraw)
            print "Code:",code
            print "Payload:",payload
            print "Fitbit:",authraw
            print "Base64Auth:",b64auth
            print "----SENDING TOKEN REQUEST----"
            response=requests.post("https://api.fitbit.com/oauth2/token",
                                   data=payload,
                                   headers={"Authorization":b64auth,"Content-Type":"application/x-www-form-urlencoded"})
            print response.text
            print response.headers
            self.wfile.write("HTTP/1.0 200 OK\nContent-Type: text/html")

        for t in THRESHOLDS:
            if t[0] in self.data:
                trysite = t
                break
        dt=self.rfile.read()
        print dt
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
    import os.path
    try:
        if not os.path.isfile("/etc/hosts.backup"):
            cp["/etc/hosts", "/etc/hosts.backup"]()
        thread.start_new_thread(updateLoop, ())
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
