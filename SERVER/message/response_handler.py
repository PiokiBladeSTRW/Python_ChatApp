#Header
from server_state import state
import message.message_handler as message_handle
import message.system_handler as system_handler


'''Handle user heartbeats- Ensuring the Client is Alive'''
def heartbeats() -> tuple: 
    return ('*', '/hbp')   


'''Handle regular old messages'''
def handle_messages(response:dict) -> tuple: 
    # Seperately Handle Room and Normal Messages

    if(response['receiver_id'].startswith('room_')):
        return message_handle.room_handle(response)    
    else:
        return message_handle.dm_handle(response) 


'''Handle system messages, that is, commands'''
def system(clientSock:object, response:dict) -> tuple: 

    # Obtain Command and execute according function
    command = response['command']    
    if (command == state.client_codes['user_exit']):    return system_handler.user_exit()
    if (command == state.client_codes['room_join']):    return system_handler.room_join(clientSock, response)
    if (command == state.client_codes['room_create']):  return system_handler.room_create(clientSock, response)
    if (command == state.client_codes['room_invite']):  return system_handler.room_invite(response)
    if (command == state.client_codes['room_admin']):   return system_handler.room_admin(response)
    if (command == state.client_codes['room_demote']):  return system_handler.room_demote(response)
    if (command == state.client_codes['room_kick']):    return system_handler.room_kick(response)
    if (command == state.client_codes['room_ban']):     return system_handler.room_ban(response)    
    if (command == state.client_codes['room_unban']):   return system_handler.room_unban(response)  
    if (command == state.client_codes['room_transfer']):return system_handler.transfer(response)
    if (command == state.client_codes['room_leave']):   return system_handler.room_leave(response)
    if (command == state.client_codes['user_join']):    return system_handler.user_join(clientSock, response)

    raise ValueError(f"●→INVALID COMMAND RECEIVED: {command}")


'''----------------------------------------------'''


'''Parse Response Received by Clients'''
def parse_response( clientSock:object, response:dict) -> tuple:

    if(response['type'] == state.msgTypes['heartbeat']):
        return heartbeats()        

    if(response['type'] == state.msgTypes['message']):
        return handle_messages(response)

    if(response['type'] == state.msgTypes['system']):
        return system(clientSock, response)
    
    raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")

'''
RETURN FORMAT: (DESTINATION, PAYLOAD, STATE)
    receiver_id: 
        '/.'     : All Online
        'room_'  : All in a Room            [returns uuid]   
        '/s'     : User Alert   
        'user_'  : Specific Username        [returns uuid]
        '*'      : Special Case, Need Handling
        None     : No Sending Data         
'''