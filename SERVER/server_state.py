'''Global Variables of the Server'''

#Header
import json

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

    '''Function Handling Json Data Writing'''
    def write_json(self, filePath, data_write): 

        with open(filePath, 'w') as fileHandler:
            json.dump(data_write, fileHandler)

    # '''Function Handling one key JSON data Loading'''
    # def read_json_key(self, filePath, key): 
        
    #     with open(filePath, 'r') as fileHandler:
    #         fileData= json.load(fileHandler)
    #         return fileData[key]
    
    '''Function Handling entire JSON load'''
    def read_json(self, filePath):

        with open(filePath, 'r') as fileHandler:
            return json.load(fileHandler)