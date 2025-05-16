'''Handle (bring about requried changes) and Display Incoming Data from Server'''

#Header
import formatting
import time

import interface.msg as msg
import interface.sys as sys
from session_state import state

'''Handle Default Messages'''
async def incoming_message(response:dict):    
    if( type(response['sender_id']) == list):         
        await msg.rooms(response)

    else:
        await msg.dms(response)

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
    
    

'''-------------------------------------'''


'''Handle Responses'''
async def parse_response(response:dict): 
    # For future purpose of Storing in DB
    if(not response.get('timestamp')): response['timestamp'] = time.time()

    if(response['type'] == state.msgTypes['message']):
        await incoming_message(response)

    elif(response['type'] == state.msgTypes['system']):
        system(response)
      
    else:         
        raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")