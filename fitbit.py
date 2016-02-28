from threadvar import ThreadVar
from firebase import firebase
import webbrowser
import json
import requests
import time

class FitBit:
    creds = json.loads(open('auth.json','r').read())
    steps = ThreadVar(0)
    goal = ThreadVar(0)
    firebase = firebase.FirebaseApplication(
        'https://torrid-torch-8987.firebaseio.com/',
    None)
    access_token = None
    refresh_token = None
    user_id = None
    
    @staticmethod
    def storeLogin(login):
        if 'success' in login:
            if not login["success"]:
                print "----UNSUCCESSFUL AUTH----"
                return
        login['time'] = time.time()
        FitBit.firebase.put('/',None,login)
        FitBit.setLogin(login)

    @staticmethod
    def setLogin(login):
        FitBit.access_token = login['access_token']
        FitBit.refresh_token = login['refresh_token']
        FitBit.user_id = login['user_id']
        
    @staticmethod
    def tryLogin():
        login_url = "https://fitbit.com/oauth2/authorize?client_id=" + FitBit.creds["client_id"] +  "&response_type=code&scope=activity&redirect_uri=http://localhost/fitbit&expires_in=86400"

        result = FitBit.firebase.get('/', None)
        if not 'access_token' in result or \
           not 'time' in result or \
           time.time() - result['time'] > 3600:
            webbrowser.open(login_url)
        else:
            FitBit.storeLogin(result)

    @staticmethod
    def pullFromServer():
        result = FitBit.firebase.get('/', None)
        if not 'access_token' in result or \
           not 'time' in result or \
           time.time() - result['time'] > 3600:
            print "Cannot pull: access token not set or is expired"
            return
        url="https://api.fitbit.com/1/user/-/activities/date/2016-02-27.json"
        auth=result['token_type']+" "+result['access_token']
        response=requests.get(url,
                              headers={"Authorization":auth})
        print response.text
        parsed = json.loads(response.text)
        FitBit.steps.setVal(parsed['summary']['steps'])
        FitBit.goal.setVal(parsed['goals']['steps'])
        print "Set steps={} goal={}".format(FitBit.steps.getVal(), FitBit.goal.getVal())
