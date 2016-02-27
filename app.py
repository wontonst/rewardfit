import thread
import time
from firebase import firebase
from plumbum import local
from plumbum.cmd import cp, echo

resetHost = cp['/etc/hosts.backup', '/etc/hosts']
PULL_RATE=2500
PORT = 8000
firebase = firebase.FirebaseApplication(
    'https://torrid-torch-8987.firebaseio.com/',
    None)

def runServer():
    import SimpleHTTPServer
    import SocketServer
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "serving at port", PORT
    httpd.serve_forever()

def pullFromServer():
    result = firebase.get('/',None)
    return result['steps']

def generateSite(raw_steps):
    from jinja2 import Template
    template = Template(
        open('template.html', 'r').read()
        )
    open('index.html','w+').write(template.render(steps=raw_steps))
    
def genSiteDaemon():
    # Can't use firebase.on() so we have to just pull every PULL_RATE
    # ms
    while True:
        print "Pulling..."
        raw = pullFromServer()
        generateSite(raw)
        time.sleep(PULL_RATE)

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

if __name__ == "__main__":
    thread.start_new_thread(runServer, ())
    genSiteDaemon()
