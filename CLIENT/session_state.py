'''Holds Global Variable per session'''

# Header
import time
import json
from loguru import logger

class ClientState:
    def __init__(self):
        self.clientUUID = ''
        self.receiver = ''
        self.pReceiver = ''
        self.clientSock = None
        self.clientRoomsFile = []
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

            "er_Invalid_login": 201,
            "er_Exists_username": 202,
            "er_Not_admin": 203,
            "er_Not_room_member": 204,
            "er_Room_exists": 205,
            "er_Member_in_room": 206,
            "er_Member_is_admin": 207,
            "er_Invalid_user": 208,
            'er_Invalid_room': 209,
            'er_Not_in_room': 210            
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
            110 : "{1} has been Kicked from {0}",
            111 : "{1} has been Banned from {0}",

            201 : "Invalid Login Credentials",
            202 : "Username already in Use",            
            203 : "You are not an Admin",
            204 : "You are not a Member of this Room",
            205 : "This Room Already Exists",
            206 : "Member already in room",
            207 : "Member already admin",
            208 : "The user doesn't exist",
            209 : "The room doesn't exist",
            210 : "The Member isn't in Room"            
        }
        self.sys_format = (101,104,105,106,107)
        self.receiver_change_codes = (101,208)
        self.receiver_force_change_codes = (204, 205, 209)
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
            'room_ban' : 9
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
        with open(f"rooms/{clientProfile}.json", 'r') as roomsHandler:
            data = json.load(roomsHandler)
            self.clientRoomsFile = data['rooms']

    '''Encode the data'''
    def encode(self, payload:tuple):

        # Data always to be sent regardless of Type
        data = {
                "sender": self.clientUUID,                      
                "content": payload[0], 
                "type": payload[1]
            }
        
        # Additional Data Entries
        if(data['type'] in ('msg')):
            data['receiver'] = self.receiver
            data['timestamp'] = str(time.time())
        
        elif(data['type'] == 'sys'):
            #payload[0] = (command_code, arguments)
            data["command"] = payload[0][0]
            data["content"] = payload[0][1]

        '''
        Message Format: {"sender": <username>, 
                        "receiver": <username>,
                        "command" : <command_code>,
                        "content": '--', 
                        "type": 'msg/..',
                        "timestamp": "[Hour:Minute]"}     

        Types:
        ->msg: Default String Message
        ->sys: System Message / Commands
        ->hbp: Heartbeat Pings. Letting Server know you are there.
        ->con: Displays new users logins
        '''   

        return json.dumps(data)
    
    '''Change Receivers'''
    def receiver_change(self, receiver, update_past = True):           
        if(update_past): 
            self.pReceiver = self.receiver
        self.receiver = receiver        
        
        if(receiver==''): receiver = 'No One'

        self.log(f"Changed Receiver to {receiver}")
        
        if(receiver.startswith('/r')):
            print('', "="*25, f"Now Chatting in {receiver[2::]}", "="*25, sep='\n')
            return

        print('', "="*25, f"Now Chatting with {receiver}", "="*25, sep='\n')

    '''Log Something'''
    def log(self, msg):
        logger.opt(depth=1).info(msg)

state = ClientState()