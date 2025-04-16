'''Mini Functions grouped together that can be utilized'''

# Header
import time
import json

def encode(payload:tuple, state:object):
    
    '''
    Message Format: {"sender": <username>, 
                    "receiver": <username>, 
                    "content": '--', 
                    "type": 'msg/..',
                    "timestamp": "[Hour:Minute]"}     

    Types:
    ->msg: Default String Message
    ->usr: Entry of Username / Retrieval of '<> IS ONLINE'
    ->sys: System Message / Commands
    ->hbp: Heartbeat Pings. Letting Server know you are there.
    ->auth: Handles Authentication of User
    '''    

    timestamp = str(time.time())

    data = {"sender": state.clientUsrn, 
            "receiver": state.receiver, 
            "content": payload[0], 
            "type": payload[1],
            "timestamp": timestamp}
    
    if(type in ('usr', 'sys', 'hbp')):
        data.pop('receiver')
        data.pop('timestamp')

    return json.dumps(data)