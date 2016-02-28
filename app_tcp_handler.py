import SocketServer
import base64
import requests
import json
from jinja2 import Template
from app_constants import AppConstants
from fitbit import FitBit

class AppTCPHandler(SocketServer.StreamRequestHandler):
    last_code = None
    def handleFitbit(self):
        print "----HANDLING FITBIT OAUTH REQUEST----"
        code = self.data[self.data.find("code")+5:self.data.find("HTTP")-1]
        if code == AppTCPHandler.last_code:
            print "----IGNORING DUPLICATE----"
            retval=self.generateClosePage()
            print retval
            self.wfile.write(retval)
            return
        print "{} and {} are not equal".format(code,AppTCPHandler.last_code)
        AppTCPHandler.last_code = code
        payload={"grant_type":"authorization_code",
                 "client_id":FitBit.creds['client_id'],
                 "redirect_uri":"http://localhost/fitbit",
                 "code":code}
        authraw="{}:{}".format(FitBit.creds['client_id'], FitBit.creds['client_secret'])
        b64auth="Basic "+base64.b64encode(authraw)
        print "Code:",code
        print "Payload:",payload
        print "Fitbit:",authraw
        print "Base64Auth:",b64auth
        print "----SENDING TOKEN REQUEST----"
        response=requests.post("https://api.fitbit.com/oauth2/token",
                               data=payload,
                               headers={"Authorization":b64auth,"Content-Type":"application/x-www-form-urlencoded"})
        print response.headers
        print response.text
        parsed = json.loads(response.text)
        FitBit.storeLogin(parsed)
        retval=self.generateClosePage()
        FitBit.pullFromServer()
        print retval
        self.wfile.write(retval)
        
    def handle(self):
        trysite=None
        self.data = self.request.recv(2048)
        print self.data
        
        if "GET /fitbit?code=" in self.data:
            self.handleFitbit()
            return

        print "----GENERATING WEBSITE---"
        for t in AppConstants.THRESHOLDS:
            if t[0] in self.data:
                trysite = t
                break

        retval=self.generateSite(trysite)
        print retval
        self.wfile.write(retval)
        print "----REQUEST COMPLETE----"
        
    def generateSite(self, site):
        """Generate site based on steps and URL being visited"""
        template = Template(
            open('template.html', 'r').read()
        )
        print FitBit.steps
        print "Generating with steps={} site={} goal={}".format(FitBit.steps.getVal(), site, FitBit.goal.getVal())
        return template.render(steps=FitBit.steps.getVal(), site=site, goal=FitBit.goal.getVal())

    def generateClosePage(self):
        """Generates a site that just closes itself (for auth purposes)"""
        template = Template(
            open('close.html', 'r').read()
        )
        return template.render()
