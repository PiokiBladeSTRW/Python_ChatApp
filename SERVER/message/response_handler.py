#Header
import message.auth_handle as auth_handle
import message.message_handler as message_handle
import message.system_handler as system_handler

'''Handle user heartbeats- Ensuring the Client is Alive'''
def heartbeats(clientSock:object, response:dict, state:object) -> tuple: 
    #Nothing to do here, main class adds time to timeout
    return ('*', '/hbp', state)   

'''Handle User Authentication'''
def authentication(clientSock:object, response:dict, state:object) -> tuple:
    #Content Format: {Action: <>, Username: <>, Passwd: <>, Email: <>}
    content = response['content']    
    
    # If Relog
    if(content['username'] in state.uuidsFile):
        if(state.uuidsFile[content['username']] in state.uuid_sock):
            content['action'] = 'relog'

    # Confirm Authentication
    data= auth_handle.parse_authentication(clientSock, content, state)

    if(data == True):
        return ('*', '/logged', state)
      
    return data

'''Handle regular old messages'''
def handle_messages(clientSock:object, response:dict, state:object) -> tuple: 
    # Seperately Handle Room and Normal Messages
    if(response['receiver'].startswith('/r')):
        return message_handle.room_handle(clientSock, response, state)    
    else:
        return message_handle.dm_handle(response, state)
    
def system(clientSock:object, response:dict, state:object) -> tuple: 
    # Obtain Command
    content = response['content']

    match content[:2]:
        case '/e': return system_handler.user_exit(state)
        case '/o': return system_handler.online_list(response, state)
        case '/r': return system_handler.room_list(state)
        case '/c': return system_handler.create_room(clientSock, response, state)
        case '/i': return system_handler.room_invite(response, state)
        case '/a': return system_handler.room_admin(response, state)

'''Parse Response Received by Clients'''
def parse_response( clientSock:object, response:dict, state:object) -> tuple:

    if(response['type'] in types): 
        data = types[response['type']](clientSock, response, state)
        return data  
    else:
        raise Exception("●→INVALID MESSAGE TYPE RECEIVED")

'''Response Types'''
types ={
    'hbp': heartbeats,
    'auth': authentication,
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