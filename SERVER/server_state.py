'''Global Variables of the Server'''
class ServerState:
    def __init__(self):
        self.sock_user= {}             # socket : username
        self.user_sock = {}            # username : socket       
        self.timeout= {}               # socket: last heartbeat        
        self.rooms= {}                 # room name : [sockets]
        self.sock_room = {}            # socket : room

        '''Codes for System Messages. 'er' prefix for Errors'''
        self.codes ={            
            "user_exit": 101,
            "relog_begin": 102,
            "relog_finish": 103,
            "er_Invalid_login": 201,
            "er_Exists_username": 202
        }           
