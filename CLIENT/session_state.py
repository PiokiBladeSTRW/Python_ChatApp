'''Holds Global Variable per session'''
class ClientState:
    def __init__(self):
        self.clientUsrn = ''
        self.receiver = ''
        self.pReceiver = ''
        self.clientSock = None

        self.msgTypes= {
            "message": "msg",            
            "system": "sys",
            "heartbeat": "hbp",
            "authentication": "auth"
        }

        self.system_codes ={
            101 : "",
            102 : "OLD SESSION LIVE; FORCE CLOSING..",
            103 : "SUCCESSFUL RELOG!",            
            104 : "You are not a Member of this Room",
            201 : "Invalid Login Credentials",
            202 : "Username already in Use",
            203 : "The Room does not Exist"
        }