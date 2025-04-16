'''Holds Global Variable per session'''
class clientState:
    def __init__(self):
        self.clientUsrn = ''
        self.receiver = ''
        self.pReceiver = ''
        self.clientSock = None