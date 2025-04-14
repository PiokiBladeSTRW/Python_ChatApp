def encode(payload, state):
    '''
    Types:
    ->msg: Default String Message
    ->usr: Entry of Username / Retrieval of '<> IS ONLINE'
    ->sys: System Message / Commands
    ->hbp: Heartbeat Pings. Letting Server know you are there.
    '''
    
    timestamp = str(time.time())

    data = {"sender": state['clientUsrn'], 
            "receiver": state['receiver'], 
            "content": payload[0], 
            "type": payload[1],
            "timestamp": timestamp}
    
    if(type in ('usr', 'sys', 'hbp')):
        data.pop('receiver')
        data.pop('timestamp')

    return json.dumps(data)

import time
import json