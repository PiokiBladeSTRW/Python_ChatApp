'''Holds Global Variable per session'''

# Header
import time
import json

class ClientState:
    def __init__(self):
        self.clientUUID = ''
        self.receiver = ''
        self.pReceiver = ''
        self.clientSock = None

        with open("rooms.json", 'r') as roomsHandler:
            data = json.load(roomsHandler)
            self.clientRoomsFile = data['rooms']

        self.msgTypes= {
            "message": "msg",            
            "system": "sys",
            "heartbeat": "hbp",
            "authentication": "auth"
        }

        self.system_codes ={
            101 : "",
            102 : "OLD SESSION LIVE; FORCE CLOSING..",
            103 : "SUCCESSFUL RELOG!",            
            104 : "You are not a Member of this Room",
            105 : "Joined the Room",
            201 : "Invalid Login Credentials",
            202 : "Username already in Use",
            203 : "The Room does not Exist",
            204 : "You are not an Admin"
        }

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
        timestamp = str(time.time())

        data = {"sender": self.clientUUID, 
                "receiver": self.receiver,                 
                "content": payload[0], 
                "type": payload[1],
                "timestamp": timestamp}
        
        if(data['type'] in ('auth', 'sys', 'hbp')):
            data.pop('receiver')
            data.pop('timestamp')
        
        if(data['type'] == 'sys'):
            data["command"] = payload[0][0]
            data["content"] = payload[0][1]

        '''
        Message Format: {"sender": <username>, 
                        "receiver": <username>,
                        "command" : <command code>,
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