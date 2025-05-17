# Header
import json
import requests
from loguru import logger

class ClientState:
    '''Class to hold all Global Variables and Functions'''

    def __init__(self):
        self.clientUUID = ''
        self.receiver_id = ''
        self.preceiver_id = ''
        self.clientSock = None        
        self.clientProfile = ''

        # Mapped-Values to avoid Magic Values
        self.msgTypes= {
            "message": "msg",            
            "system": "sys",
            "heartbeat": "hbp"
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
            "room_members":115, 
            "member_demote":116,  
            'member_owner': 117,
            'new_owner': 118,
            'user_join': 119,
            'member_left': 120,

            "er_Invalid_login": 201,
            "er_Exists_username": 202,
            "er_Not_admin": 203,
            "er_Not_room_member": 204,
            "er_Room_exists": 205,
            "er_Member_in_room": 206,
            "er_Member_is_admin": 207,        
            'er_Member_not_ban' : 211,
            'er_Member_not_admin': 212,
            'er_Member_owner' : 213,
            'er_Not_owner': 214,

            'no_display': 300,
            'room_data' : 301,
            'room_left' : 302,
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
            115 : "0",
            116 : "Removed {1} as Admin",
            117 : "You are the OWNER of the Room",
            118 : "{1} IS NOW THE OWNER OF ROOM",
            119 : "{0} is ONLINE",
            120 : "{1} has Left {0}",

            201 : "Invalid Login Credentials",
            202 : "Username already in Use",            
            203 : "You are not an Admin",
            204 : "You are not a Member of this Room",
            205 : "This Room Already Exists",
            206 : "Member already in room",
            207 : "Member already admin",
            210 : "The Member isn't in Room",
            211 : "The Member isn't Banned",
            212 : "The Member isn't an Admin",
            213 : "The Member is the Room Owner",
            214 : "You are not the OWNER of the Room" 
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
            'room_demote': 9,
            'room_transfer': 10,
            'room_leave': 11,
            'user_join': 12,
        }

        self.sys_format = (101,104,105,106,107, 110, 111, 112, 113, 114, 115, 116, 118, 119, 120)
        self.sys_uuid_format = (101, 104, 107,110,111,112,113,114)     
        self.modify_codes = (101, 104, 105, 112, 113, 204, 205, 300, 301, 302)

    
    def profileBased(self, clientProfile):
        '''Tasks that requires clientProfile'''

        self.clientProfile = clientProfile

        # Log Setup
        logger.remove()
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

        # Files Setup
        with open(f"client_data/rooms/{clientProfile}.json", 'r') as roomsHandler:
            self.roomsFile: dict = json.load(roomsHandler)

        with open(f"client_data/uuid_map/{clientProfile}.json", 'r') as uuidHandle:
            self.uuidsFile: dict = json.load(uuidHandle)
        
        # Reverse Dictionary
        self.name_uuid_dict=  {}
        for uuid in self.uuidsFile:
            self.name_uuid_dict[self.uuidsFile[uuid]] = uuid

    
    def encode(self, payload:tuple, time:float = 0):
        '''
        Encode the Payload Appropriately
        Payload = (Content, Type) [or ( (Command, Arguments+), Type)]
                  
        Message Fields:
            sender_id    = UUID of sender_id
            receiver_id  = UUID of receiver_id            
            command     = Command Code
            content     = Command Arguments in case of Command
            timestamp   = Epoch timestamp
            type        = Distinguishing different forms of Data

        Types:
        ->msg: Default String Message
        ->sys: System Message / Commands
        ->hbp: Heartbeat Pings. Letting Server know you are there.        
          
        '''

        # Data always to be sent regardless of Type
        data = {
                "sender_id": self.clientUUID,                      
                "content": payload[0], 
                "type": payload[1]
            }

        # Additional Data Entries
        if(data['type'] in (self.msgTypes['message'])):
            data['receiver_id'] = self.receiver_id
            data['timestamp'] = str(time)
        
        elif(data['type'] == self.msgTypes['system']):
            #payload[0] = (command_code, arguments)
            data["command"] = payload[0][0]
            data["content"] = payload[0][1]

            if(self.receiver_id.startswith('room_')): data['receiver_id'] = self.receiver_id            
            if(data['content'] == ''): data.pop('content') 

        return json.dumps(data)
    

    def receiver_id_change(self, receiver, update_past = True):   
        '''Change receiver_ids'''    

        if(update_past): 
            self.preceiver_id = self.receiver_id

        self.receiver_id = receiver       
        
        # Display
        if(receiver==''): receiver = 'No One'
        else : receiver = state.uuidsFile[receiver]

        self.log(f"Changed receiver_id to {receiver}")        

        print('', "="*25, f"Now Chatting with {receiver}", "="*25, sep='\n')

    
    def log(self, msg):
        '''Log Something'''
        logger.opt(depth=1).info(msg)


    def name_uuid(self, name: str) -> str:
        '''Convert a Name to UUID; Either Locally Mapped or Requested by Server'''

        state.log(f"Converting {name} to UUID")

        if(name in state.name_uuid_dict): 
            return state.name_uuid_dict[name]
        
        else:
            uuid = requests.get(f"http://127.0.0.1:8000/name_to_uuid/{name}").json()['content']
            if(uuid == 0):
                print("{System}: Account/Room of such Name doesn't Exist")
                return 0
            
            # Updated Local Mapping
            state.log(f"Updated UUIDs file with {uuid}:{name}")
            state.uuidsFile[uuid] = name
            state.name_uuid_dict[name] = uuid
            return uuid
        
    def uuid_name(self, uuid: str) -> str:
        '''Convert a UUID to Name; Either Locally Mapped or Requested by Server'''
        state.log(f"Converting {uuid} to Name")

        if(uuid in state.uuidsFile): 
            return state.uuidsFile[uuid]
        
        else:
            name = requests.get(f"http://127.0.0.1:8000/uuid_to_name/{uuid}").json()['content']

            # Updated Local Mapping
            state.log(f"Updated UUIDs file with {uuid}:{name}")            
            state.uuidsFile[uuid] = name
            state.name_uuid_dict[name] = uuid
            return name

#__MAIN__
state = ClientState()