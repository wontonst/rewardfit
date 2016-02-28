import SimpleHTTPServer
import SocketServer
from app_constants import AppConstants
from app_tcp_handler import AppTCPHandler


# Every hackathon I use a huge web framework yada yada yada. Well this
# time I'm going to write my own bare metal server.

class AppServer:

    def __init__(self):
        SocketServer.TCPServer.allow_reuse_address = True
        self.httpd = SocketServer.TCPServer(("", AppConstants.PORT), AppTCPHandler)

    def runServer(self):
        print "Server starting on port", AppConstants.PORT
        self.httpd.serve_forever()

    def killServer(self):
        self.httpd.server_close()
