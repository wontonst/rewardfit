from plumbum import local
from plumbum.cmd import cp, echo, ls
cp = local["cp"]
resetHost = cp['/etc/hosts.backup', '/etc/hosts']

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
    resetHost()
    block(1000)
