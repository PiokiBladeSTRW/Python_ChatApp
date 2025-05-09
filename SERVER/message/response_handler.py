#Header
from server_state import state
import json
import message.message_handler as message_handle
import message.system_handler as system_handler

'''Handle user heartbeats- Ensuring the Client is Alive'''
def heartbeats(clientSock:object, response:dict) -> tuple: 
    #Nothing to do here, main class adds time to timeout
    return ('*', '/hbp')   

'''Handle connecting User to server'''
def connect(clientSock:object, response:dict) -> tuple:
    user_uuid = response['sender_id']

    if(user_uuid in state.uuid_sock):
        state.log(f"User Relogging: {user_uuid}")
        return ('*', '/relog')

    state.log(f"User Joined: {user_uuid}")
    state.uuid_sock[user_uuid] = clientSock
    state.sock_uuid[clientSock] = user_uuid
    state.sock_rooms[clientSock] = []

    for room in state.accountsFile[user_uuid]['rooms']:
        state.room_sock[room].append(clientSock)                
        state.sock_rooms[clientSock].append(room)

    return ('/.', json.dumps({"sender_id": user_uuid,"type": "con" }))

'''Handle regular old messages'''
def handle_messages(clientSock:object, response:dict) -> tuple: 
    # Seperately Handle Room and Normal Messages
    if(response['receiver'].startswith('room_')):
        return message_handle.room_handle(response)    
    else:
        return message_handle.dm_handle(response) 

'''Handle system messages, that is, commands'''
def system(clientSock:object, response:dict) -> tuple: 
    # Obtain Command
    command = response['command']    
    if (command == state.client_codes['user_exit']):    return system_handler.user_exit()
    if (command == state.client_codes['online_list']):  return system_handler.online_list(response)
    if (command == state.client_codes['rooms_list']):   return system_handler.room_list()
    if (command == state.client_codes['room_join']):    return system_handler.room_join(clientSock, response)
    if (command == state.client_codes['room_create']):  return system_handler.room_create(clientSock, response)
    if (command == state.client_codes['room_invite']):  return system_handler.room_invite(response)
    if (command == state.client_codes['room_admin']):   return system_handler.room_admin(response)
    if (command == state.client_codes['room_kick']):    return system_handler.room_kick(response)
    if (command == state.client_codes['room_ban']):     return system_handler.room_ban(response)
    if (command == state.client_codes['room_members']): return system_handler.room_members(response)
    if (command == state.client_codes['room_unban']):   return system_handler.room_unban(response)
    if (command == state.client_codes['profile_get']):  return system_handler.profile_get(response)
    if (command == state.client_codes['profile_set']):  return system_handler.profile_set(response)
    if (command == state.client_codes['room_desc']):    return system_handler.room_desc(response)
    if (command == state.client_codes['room_info']):    return system_handler.room_info(response)    

    raise ValueError(f"●→INVALID COMMAND RECEIVED: {command}")


'''----------------------------------------------'''


'''Parse Response Received by Clients'''
def parse_response( clientSock:object, response:dict) -> tuple:

    if(response['type'] in types): 
        data = types[response['type']](clientSock, response)        
        return data  
    else:
        raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")

'''Response Types'''
types ={
    'hbp': heartbeats,
    'con': connect,
    "msg": handle_messages,
    "sys": system    
}

'''
RETURN FORMAT: (DESTINATION, PAYLOAD, STATE)
    RECEIVER: 
        '/.'     : All Online
        '/r--'  : All in a Room        
        '/s'    : User Alert   
        '<user>': Specific Username
        '*'     : Special Case, Need Handling
        None    : No Sending Data         
'''