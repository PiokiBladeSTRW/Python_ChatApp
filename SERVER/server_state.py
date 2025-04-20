'''Global Variables of the Server'''

#Header
import json

class ServerState:
    def __init__(self):
        self.sock_uuid= {}              # socket : uuid
        self.uuid_sock = {}             # uuid : socket       
         
        self.sock_rooms = {}            # socket : [rooms]                  -Auth
        self.room_socks= {}             # room name : [sockets]             -State
        self.room_invites = {}          # room name : [invited sockets]     - Volatile

        self.timeout= {}                # socket: last heartbeat  
        
        with open("accounts.json", 'r') as fileHandle:
            self.accountsFile = json.load(fileHandle)
            
        with open("uuids.json", 'r') as fileHandle:
            self.uuidsFile = json.load(fileHandle)

        with open ("rooms.json", 'r') as fileHandle:
            self.roomsFile = json.load(fileHandle)

        for room in self.roomsFile:
            self.room_socks[room] = []
            self.room_invites[room] = []

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

    def uuid_user(self, uuid):
        return self.accountsFile[uuid]['username']