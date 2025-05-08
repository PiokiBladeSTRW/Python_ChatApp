'''Global Variables of the Server'''

#Header
import json
from loguru import logger

class ServerState:
    def __init__(self):
        self.sock_uuid= {}              # socket : uuid
        self.uuid_sock = {}             # uuid : socket       
         
        self.sock_rooms = {}            # socket : [rooms]                  -Auth
        self.room_sock= {}             # room name : [sockets]             -State
        self.timeout= {}                # socket: last heartbeat  
        
        with open("accounts.json", 'r') as fileHandle:
            self.accountsFile = json.load(fileHandle)
            
        with open("uuids.json", 'r') as fileHandle:
            self.uuidsFile = json.load(fileHandle)

        with open ("rooms.json", 'r') as fileHandle:
            self.roomsFile = json.load(fileHandle)            

        for room in self.roomsFile:
            self.room_sock[room] = []

        logger.remove()
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss} </green> |"
            "<level>{level: <8}</level> |"
            "<cyan>{module}</cyan> : <cyan>{function}</cyan> -"
            "<level>{message}</level>"
        )
        logger.add(
            "logs/log.log",
            mode= 'w',            
            level = "INFO",
            format = log_format,
            encoding= 'utf-8'            
        )

        '''Codes for System Messages. 'er' prefix for Errors'''
        self.system_codes ={            
            "user_exit": 101,
            "relog_begin": 102,
            "relog_finish": 103,        
            "new_room_member": 104,
            "room_live": 105,
            "room_invite": 106,
            "member_admin": 107,
            "account_risk": 108,
            "session_active": 109,
            "member_kick": 110,
            "member_ban": 111,
            "got_kicked": 112,
            "got_banned": 113,
            "member_unban":114,

            "er_Invalid_login": 201,
            "er_Exists_username": 202,
            "er_Not_admin": 203,
            "er_Not_room_member": 204,
            "er_Room_exists": 205,
            "er_Member_in_room": 206,
            "er_Member_is_admin": 207,
            "er_Invalid_user": 208,
            'er_Invalid_room': 209,
            'er_Not_in_room': 210, 
            'er_Member_not_ban' : 211
        }

        self.client_codes ={
            'user_exit': 1,
            'online_list': 2,
            'rooms_list': 3,
            'room_join': 4,
            'room_create': 5,
            'room_invite': 6,
            'room_admin' : 7,
            'room_kick' : 8,
            'room_ban' : 9,
            "room_members" : 10,
            'room_unban' : 11,
            'profile_get': 12,
            'profile_set': 13,
            'room_desc': 14,
            'room_info': 15,
        }


    def uuid_user(self, uuid:str):
        return self.accountsFile.get(uuid)['username']
    
    def user_uuid(self, user:str):        
        return self.uuidsFile.get(user)['uuid']
    
    def log(self, msg:str):
        logger.opt(depth=1).info(msg)
    
state = ServerState()