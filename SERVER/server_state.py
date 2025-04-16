'''Global Variables of the Server'''
class serverState:
    def __init__(self):
        self.sock_user= {}             # socket : username
        self.user_sock = {}            # username : socket       
        self.timeout= {}               # socket: last heartbeat        
        self.rooms= {}                 # room name : [sockets]
        self.sock_room = {}            # socket : room