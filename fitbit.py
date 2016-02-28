from threadvar import ThreadVar
from firebase import firebase

class FitBit:
    steps = ThreadVar(0)
    firebase = firebase.FirebaseApplication(
        'https://torrid-torch-8987.firebaseio.com/',
    None)

    @staticmethod
    def pullFromServer():
        result = FitBit.firebase.get('/',None)
        return result['steps']
    
