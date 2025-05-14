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

        self.username_uuid = {}             # Username : UUID [Stored only in Memory]
        self.roomName_roomUuid = {}     # Room Name : Room UUID [Stored Only in Memory]
        
        with open("accounts.json", 'r') as fileHandle:
            self.accountsFile: dict = json.load(fileHandle)
            
        with open("acc_uuids.json", 'r') as fileHandle:
            self.uuidsFile: dict = json.load(fileHandle)

        with open ("rooms.json", 'r') as fileHandle:
            self.roomsFile: dict = json.load(fileHandle)    

        for room in self.roomsFile:
            self.room_sock[room] = []


        for uuid in self.accountsFile:
            self.username_uuid[self.accountsFile[uuid]['username']] = uuid

        for room_uuid in self.roomsFile:
            self.roomName_roomUuid[self.roomsFile[room_uuid]['name']] = room_uuid


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
            "member_ban" : 111,
            "got_kicked": 112,
            "got_banned": 113,
            "member_unban":114,
            "room_members":115,   
            "member_demote": 116,         

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
            'er_Member_not_ban' : 211,
            'er_Member_not_admin': 212,

            'no_display': 300
        }

        self.client_codes ={
            'user_exit': 1,           
            'room_join': 2,
            'room_create': 3,
            'room_invite': 4,
            'room_admin' : 5,
            'room_kick' : 6,
            'room_ban' : 7,            
            'room_unban' : 8, 
            'room_demote': 9
        }


    def uuid_user(self, uuid:str):
        return self.accountsFile.get(uuid)['username']
    
    def user_uuid(self, username:str):
        return self.username_uuid.get(username)
    
    def log(self, msg:str):
        logger.opt(depth=1).info(msg)
    
state = ServerState()