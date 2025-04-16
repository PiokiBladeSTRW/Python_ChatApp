'''Holds Global Variable per session'''
class clientState:
    def __init__(self):
        self.clientUsrn = ''
        self.receiver = ''
        self.pReceiver = ''
        self.clientSock = None

        self.msgTypes= {
            "message": "msg",
            "online": "usr",
            "system": "sys",
            "heartbeat": "hbp",
            "authentication": "auth"
        }