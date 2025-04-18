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

    '''Function Handling Json Data Writing'''
    def write_json(self, filePath, data_write): 

        with open(filePath, 'w') as fileHandler:
            json.dump(data_write, fileHandler)
    
    '''Function Handling entire JSON load'''
    def read_json(self, filePath):

        with open(filePath, 'r') as fileHandler:
            return json.load(fileHandler)