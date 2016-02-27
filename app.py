import thread
import threading
import time
from firebase import firebase
from plumbum import local
from plumbum.cmd import cp, echo
import SimpleHTTPServer
import SocketServer
from Tkinter import *

global email
global pwd
global user
global password

def make_entry(parent, caption, width=None, **options):
    Label(parent, text=caption).pack(side=TOP)
    entry = Entry(parent, **options)
    if width:
        entry.config(width=width)
    entry.pack(side=TOP, padx=10, fill=BOTH)
    return entry

def enter(event): 
    store_creds()

def store_creds():
    global email, pwd, user, password
    email = user.get()
    pwd = password.get()
    print email
    print pwd

def startUI():
    global user, password
    root = Tk()
    root.geometry('300x160')
    root.title('Enter your information')
    var = StringVar()
    label = Label( root, textvariable=var, relief=RAISED )
    
    var.set("Please enter your Fitbit email and password")
    label.pack()
    #frame for window margin
    parent = Frame(root, padx=10, pady=10)
    parent.pack(fill=BOTH, expand=True)
    #entrys with not shown text
    user = make_entry(parent, "Email", 16)
    password = make_entry(parent, "Password:", 16, show="*")
    #button for saving fitbit credentials for OAUTH
    b = Button(parent, borderwidth=4, text="Login", width=10, pady=8, command=store_creds)
    b.pack(side=BOTTOM)
    password.bind('<Return>', enter)
    
    user.focus_set()
    parent.mainloop()

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
    import os.path
    try:
        if not os.path.isfile("/etc/hosts.backup"):
            cp["/etc/hosts", "/etc/hosts.backup"]()
        startUI()
        thread.start_new_thread(updateLoop, ())
        runServer()
    except:
        print "Exception caught. Cleaning and closing"
        httpd.server_close()
