#Header
import formatting

import interface.msg as msg
import interface.sys as sys
from session_state import state

async def incoming_message(response:dict):  
    '''Handle Default Messages'''

    if( type(response['sender_id']) == list):         
        await msg.rooms(response)

    else:
        await msg.dms(response)


def system(response:dict):   
    '''Handle System Messages'''   

    # Non-Command Messages
    if(not response.get('command')):
        data = ('', '{System}', response['content']) 

        print(formatting.format(data, ('s', 'cl', 'c')))           
        return    
    
    # If To-Be Kicked
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


'''Handle (bring about requried changes) and Display Incoming Data from Server'''

async def parse_response(response:dict): 
    '''Entry Function; Async purely to incorporate SQL'''    

    if(response['type'] == state.msgTypes['message']):
        await incoming_message(response)

    elif(response['type'] == state.msgTypes['system']):
        system(response)
      
    else:         
        raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")