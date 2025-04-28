'''Holds Global Variable per session'''

# Header
import time
import json

class ClientState:
    def __init__(self, clientName):
        self.clientUUID = ''
        self.receiver = ''
        self.pReceiver = ''
        self.clientSock = None

        with open(f"rooms/{clientName}.json", 'r') as roomsHandler:
            data = json.load(roomsHandler)
            self.clientRoomsFile = data['rooms']

        self.msgTypes= {
            "message": "msg",            
            "system": "sys",
            "heartbeat": "hbp",
            "authentication": "auth"
        }

        self.system_codes ={            
            "user_exit": 101,
            "relog_begin": 102,
            "relog_finish": 103,        
            "new_room_member": 104,
            "room_live": 105,
            "room_invite": 106,
            "member_admin": 107,

            "er_Invalid_login": 201,
            "er_Exists_username": 202,
            "er_Not_admin": 203,
            "er_Not_room_member": 204,
            "er_Room_exists": 205,
            "er_Member_in_room": 206,
            "er_Member_is_admin": 207,
            "er_Invalid_user": 208,
            'er_Invalid_room': 209
        }
        
        self.sys_code_msg={
            101 : "{0} is OFFLINE",
            102 : "OLD SESSION LIVE; FORCE CLOSING..",
            103 : "SUCCESSFUL RELOG!",           
            104 : "{1} Joined the Room",
            105 : "Room {0} is Live",
            106 : "{0} has sent an invitation",
            107 : "Made {1} an Admin",

            201 : "Invalid Login Credentials",
            202 : "Username already in Use",            
            203 : "You are not an Admin",
            204 : "You are not a Member of this Room",
            205 : "This Room Already Exists",
            206 : "Member already in room",
            207 : "Member already admin",
            208 : "The user doesn't exist",
            209 : "The room doesn't exist"
        }
        self.sys_format = (101,104,105,106,107)

        self.client_codes ={
            'user_exit': 1,
            'online_list': 2,
            'rooms_list': 3,
            'room_join': 4,
            'room_create': 5,
            'room_invite': 6,
            'room_admin' : 7
        }

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
        ->auth: Handles Authentication of User and ONLINE displays 
        '''   

        return json.dumps(data)
    
    '''Change Receivers'''
    def receiver_change(self, receiver):
        self.pReceiver = self.receiver
        self.receiver = receiver
        
        if(receiver==''): receiver = 'No One'
        
        if(receiver.startswith('/r')):
            print('', "="*25, f"Now Chatting in {receiver[2::]}", "="*25, sep='\n')
            return

        print('', "="*25, f"Now Chatting with {receiver}", "="*25, sep='\n')