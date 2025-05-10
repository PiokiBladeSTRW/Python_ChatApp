'''Holds Global Variable per session'''

# Header
import time
import json
import requests
from loguru import logger

class ClientState:
    def __init__(self):
        self.clientUUID = ''
        self.receiver_id = ''
        self.preceiver_id = ''
        self.clientSock = None        
        self.clientProfile = ''

        logger.remove()
        

        self.msgTypes= {
            "message": "msg",            
            "system": "sys",
            "heartbeat": "hbp",
            "connect": "con"
        }

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
        
        self.sys_code_msg={
            101 : "{0} is OFFLINE",
            102 : "OLD SESSION LIVE; FORCE CLOSING..",
            103 : "SUCCESSFUL RELOG!",           
            104 : "{1} Joined the Room",
            105 : "Room {0} is Live",
            106 : "{0} has sent an invitation",
            107 : "Made {1} an Admin",
            108 : "Your account is at Risk; Password Compromised",
            109 : "The Session is still active, Try Again Later",
            110 : "{1} has been Kicked",
            111 : "{1} has been Banned",
            112 : "You were Kicked from {0} by {1}",
            113 : "You were Banned from {0} by {1}",
            114 : "{1} has been Unbanned",

            201 : "Invalid Login Credentials",
            202 : "Username already in Use",            
            203 : "You are not an Admin",
            204 : "You are not a Member of this Room",
            205 : "This Room Already Exists",
            206 : "Member already in room",
            207 : "Member already admin",
            208 : "The user doesn't exist",
            209 : "The room doesn't exist",
            210 : "The Member isn't in Room",
            211 : "The Member isn't Banned"          
        }
        self.sys_format = (101,104,105,106,107, 110, 111, 112, 113, 114)
        self.sys_uuid_format = (101, 104, 107,110,111,112,113,114)
        self.change_codes = (101,208, 112, 113)
        self.force_change_codes = (204, 205, 209)
        self.special_commands = (109,)        

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
            'room_members' : 10,
            'room_unban' : 11,
            'profile_get': 12,
            'profile_set': 13,
            'room_desc': 14,
            'room_info': 15
        }


    '''Tasks that requires clientProfile'''
    def profileBased(self, clientProfile):
        self.clientProfile = clientProfile

        #Log Setup
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss} </green> |"
            "<level>{level: <8}</level> |"
            "<cyan>{module}</cyan> : <cyan>{function}</cyan> -"
            "<level>{message}</level>"
        )
        logger.add(
            f"logs/log_{clientProfile}.log",
            mode= 'w',
            level = "INFO",
            format = log_format,
            encoding= 'utf-8',            
        )

        #Room Handling setup
        with open(f"client_data/rooms/{clientProfile}.json", 'r') as roomsHandler:
            self.clientRoomsFile: dict = json.load(roomsHandler)

        with open(f"client_data/uuid_map/{state.clientProfile}.json", 'r') as uuidHandle:
            self.uuidsFile: dict = json.load(uuidHandle)
        
        self.name_uuid_dict=  {}
        for uuid in self.uuidsFile:
            self.name_uuid_dict[self.uuidsFile[uuid]] = uuid

    '''Encode the data'''
    def encode(self, payload:tuple):
        #Payload = (Content, Type) [or ( (Command, Arguments+), Type)]

        # Data always to be sent regardless of Type
        data = {
                "sender_id": self.clientUUID,                      
                "content": payload[0], 
                "type": payload[1]
            }
        
        # Additional Data Entries
        if(data['type'] in ('msg')):
            data['receiver_id'] = self.receiver_id
            data['timestamp'] = str(time.time())
        
        elif(data['type'] == 'sys'):
            #payload[0] = (command_code, arguments)
            data["command"] = payload[0][0]
            data["content"] = payload[0][1]

            if(self.receiver_id.startswith('room_')): data['receiver_id'] = self.receiver_id            
            if(data['content'] == ''): data.pop('content')

        '''   
        Message Fields:
            sender_idID    = UUID of sender_id
            receiver_idID  = UUID of receiver_id
            receiver_id    = Name of receiver_id [Used in case of 'First Contact']
            command     = Command Code
            content     = Command Arguments in case of Command
            timestamp   = Epoch timestamp
            type        = Distinguishing different forms of Data

        Types:
        ->msg: Default String Message
        ->sys: System Message / Commands
        ->hbp: Heartbeat Pings. Letting Server know you are there.
        ->con: Displays new users logins
        '''   

        return json.dumps(data)
    
    '''Change receiver_ids'''
    def receiver_id_change(self, receiver, update_past = True):           
        if(update_past): 
            self.preceiver_id = self.receiver_id
        self.receiver_id = receiver       
        
        if(receiver==''): receiver = 'No One'
        else : receiver = state.uuidsFile[receiver]

        self.log(f"Changed receiver_id to {receiver}")        

        print('', "="*25, f"Now Chatting with {receiver}", "="*25, sep='\n')

    '''Log Something'''
    def log(self, msg):
        logger.opt(depth=1).info(msg)

    def name_uuid(self, name: str) -> str:
        state.log(f"Converting {name} to UUID")
        if(name in state.name_uuid_dict): 
            return state.name_uuid_dict[name]
        else:
            uuid = requests.get(f"http://127.0.0.1:8000/name_to_uuid/{name}").json()['content']
            if(uuid == 0):
                print("Account/Room of such Name doesn't Exist")
                return 0
            
            state.log(f"Updated UUIDs file with {uuid}:{name}")
            state.uuidsFile[uuid] = name
            state.name_uuid_dict[name] = uuid
            return uuid
        
    def uuid_name(self, uuid: str) -> str:
        state.log(f"Converting {uuid} to Name")
        if(uuid in state.uuidsFile): 
            return state.uuidsFile[uuid]
        else:
            name = requests.get(f"http://127.0.0.1:8000/uuid_to_name/{uuid}").json()['content']

            state.log(f"Updated UUIDs file with {uuid}:{name}")            
            state.uuidsFile[uuid] = name
            state.name_uuid_dict[name] = uuid
            return name


state = ClientState()