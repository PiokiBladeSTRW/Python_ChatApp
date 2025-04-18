'''Global Variables of the Server'''

#Header
import json

class ServerState:
    def __init__(self):
        self.sock_user= {}              # socket : username
        self.user_sock = {}             # username : socket       
         
        self.sock_room = {}             # socket : room     
        self.rooms= {}                  # room name : [sockets]
        self.room_invites = {}          # room name : [invited sockets]

        self.timeout= {}                # socket: last heartbeat  
        
        with open("accounts.json", 'r') as fileHandle:
            self.accountsFile = json.load(fileHandle)
            
        with open("uuids.json", 'r') as fileHandle:
            self.uuidsFile = json.load(fileHandle)

        '''Codes for System Messages. 'er' prefix for Errors'''
        self.codes ={            
            "user_exit": 101,
            "relog_begin": 102,
            "relog_finish": 103,            
            "not_room_member": 104,
            "er_Invalid_login": 201,
            "er_Exists_username": 202,
            "er_Invalid_room": 203,
        }