'''Global Variables of the Server'''

#Header
import json

class ServerState:
    def __init__(self):
        self.sock_uuid= {}              # socket : uuid
        self.uuid_sock = {}             # uuid : socket       
         
        self.sock_rooms = {}            # socket : [rooms]                  -Auth
        self.room_socks= {}             # room name : [sockets]             -State
        self.timeout= {}                # socket: last heartbeat  
        
        with open("accounts.json", 'r') as fileHandle:
            self.accountsFile = json.load(fileHandle)
            
        with open("uuids.json", 'r') as fileHandle:
            self.uuidsFile = json.load(fileHandle)

        with open ("rooms.json", 'r') as fileHandle:
            self.roomsFile = json.load(fileHandle)

        for room in self.roomsFile:
            self.room_socks[room] = []

        '''Codes for System Messages. 'er' prefix for Errors'''
        self.system_codes ={            
            "user_exit": 101,
            "relog_begin": 102,
            "relog_finish": 103,            
            "not_room_member": 104,
            "new_room_member": 105,
            "er_Invalid_login": 201,
            "er_Exists_username": 202,
            "er_Not_admin": 203
        }

        self.client_codes ={
            'user_exit': 1,
            'online_list': 2,
            'rooms_list': 3,
            'room_join': 4,
            'room_create': 5,
            'room_invite': 6,
            'room_admin' :7
        }


    def uuid_user(self, uuid):
        return self.accountsFile[uuid]['username']