'''Handle (bring about requried changes) and Display Incoming Data from Server'''

#Header
import formatting
import time

import interface.msg as msg
import interface.sys as sys
from session_state import state

'''Handle Default Messages'''
def incoming_message(response:dict):    
    if( type(response['sender_id']) == list):         
        msg.rooms(response)

    else:
        msg.dms(response)

'''Handle System Messages'''
def system(response:dict):       
    # Guard Clause  (if not a command)
    if(not response.get('command')):
        data = ('', '{System}', response['content']) 

        print(formatting.format(data, ('s', 'cl', 'c')))           
        return    
    
    # Guard Clause (if kicked)
    if(response['command'] == state.system_codes['session_active']): 
        state.log(f"Tried Logging with an Active Session; Disconnecting")
        print(formatting.format(('', '{System}', state.sys_code_msg[response['command']]), ('s', 'cl', 'c')))
        return 'kick'

    # Room VS Standard
    if(response.get('sender_id')): 
        sys.rooms(response)
        return    
    
    sys.std(response)    
    
    
'''Handle User Loggings'''
def online_user(response:dict):
    username = state.uuid_name(response['sender_id'])
    data = ('', username, "is ONLINE")

    # OUTPUT : [sender_id 'is Online'
    print(formatting.format(data, ('s', 'c', 'S')))    

'''-------------------------------------'''


'''Handle Responses'''
def parse_response(response:dict): 
    # For future purpose of Storing in DB
    if(not response.get('timestamp')): response['timestamp'] = time.time()

    if(response['type'] in types):          
        return types[response['type']](response)        
    else:                
        raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")
    

'''Response Types'''
types ={
    "msg": incoming_message,
    "con": online_user,
    "sys": system
}