# Header
import json
from message.catch_error import CatchError

errors = CatchError()
'''
Commands and their Arguments:
1: Exit -> None
2: Online List -> None
3: Rooms List -> None
4: Create Room -> Room_Name
5: Room Invite -> (Room Name, Username)
6: Room Admin -> (Room Name, Username)'''

def encode_payload(content=None, command:int=None, sender: str = None) -> str:
    data = {
        'command': command,
        'content': content,
        'type': 'sys',
    }
    if(sender): data['sender'] = sender
    return json.dumps(data)

def modify_room(room:str, operation: tuple, state:object, clientSock:object =None, uuid:str =None ) -> None:
    '''Types of Operation: (CREATE, JOIN, INVITE, R_INVITE, ADMIN)
    clientSock: Person using Command ;  uuid: Person on receiving End of Command'''

    # Ran By Person Creating Server
    if('CREATE' in operation):
        state.room_socks[room] = []
        state.roomsFile[room] = {'members': [], 'admins': [], 'invites': []}  

    # Ran by Person joining Server
    if('JOIN' in operation):
        state.room_socks[room].append(clientSock)
        state.sock_rooms[clientSock].append(room)       

        state.roomsFile[room]['members'].append(state.sock_uuid[clientSock])
        state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room)

    # Ran by Admin Targetted to Invitee
    if('INVITE' in operation):
        state.roomsFile[room]['invites'].append(uuid)

    # Ran by Person Joining Server
    if('R_INVITE' in operation):
        state.roomsFile[room]['invites'].remove(clientSock)

    # Ran by Admin Targetted to Member
    if('ADMIN' in operation):
        state.roomsFile[room]['admins'].append(uuid)

'''----------------------------------------------'''


'''# Lets user close safely [/exit]'''
def user_exit(state:object) -> tuple:
    return ('*', '/exit', state)

'''# Gives user a list of online members [/online]'''
def online_list(response:dict, state:object) -> tuple:
    uuid_data = list(state.uuid_sock)
    uuid_data.remove(response['sender'])
    
    user_data = (state.uuid_user(x) for x in uuid_data) 
    data = '\n'.join(user_data)    

    return ('/s', encode_payload(data), state)

'''# Gives user a list of rooms [/rooms]'''
def room_list(state:object) -> tuple:
    data = '\n'.join(state.room_socks.keys())
    return ('/s', encode_payload(data), state)


'''============================='''


'''# Join a Room [/room join]'''
def room_join(clientSock:object, response:dict, state:object) -> tuple:
    room = response['content']   

    #Not a Member of Room [BIG condition, for readability avoided CatchError()]    
    if(not(clientSock in state.room_socks[room] or clientSock in state.roomsFile[room]['invites'])):  
        return ('/s', encode_payload(command = state.system_codes['er_Not_room_member']), state)  

    modify_room(room, ('JOIN', 'R_INVITE'), state, clientSock)     

    return (f'/r{room}', 
            encode_payload( [state.uuid_user(response['sender'])], state.system_codes['new_room_member'], f'/r{room}'), 
            state)

'''# Creates a new room [/room create]'''
def room_create(clientSock:object, response:dict, state:object) -> tuple:
    room = response['content']
    
    if(data := errors.error_handle(room in state.roomsFile, 'er_Room_exists', None, state)): return data
    
    modify_room(room, ('CREATE', 'JOIN', 'ADMIN'), state, clientSock)

    return ('/s',
            encode_payload(None, state.system_codes['room_live'], f'/r{room}'),
            state)


'''============================='''


'''# Invites someone to a room [/room invite]'''
def room_invite(response:dict, state:object) -> tuple:    
    room, username = response['content'][0], response['content'][1]

    #Handle non-existent account, for now Offline
    if(data := errors.error_handle(username not in state.uuidsFile, 'er_Invalid_user',state)): return data
    uuid = state.uuidsFile[username]

    #Catch Errors
    possible_errors = {
        'user_exit': (uuid not in state.uuid_sock, username),
        'er_Not_admin': (response['sender'] not in state.roomsFile[room]['admins'], None),
        'er_Member_in_room': (
            state.uuid_sock[uuid] in state.room_socks[room] or state.uuid_sock[uuid] in state.roomsFile[room]['invites'],
            None)}      
    data = errors.multiple_error_handle(possible_errors, state)
    if(data): return data[0]

    # Modify and Send  
    modify_room(room, ('INVITE'), state, uuid= uuid)
    return (uuid, encode_payload(None, state.system_codes['room_invite'], f'/r{room}'), state)

'''# Makes someone an Admin of Room [/room admin]'''
def room_admin(response:dict, state:object) -> tuple:    
    room, username = response['content'][0], response['content'][1]

    #Handle non-existent account, for now Offline
    if(data := errors.error_handle(username not in state.uuidsFile, 'er_Invalid_user',state)): return data
    uuid = state.uuidsFile[username]       

    #Catch Errors
    possible_errors = {
        'user_exit': (uuid not in state.uuid_sock, username),
        'er_Not_admin': (response['sender'] not in state.roomsFile[room]['admins'], None),
        'er_Member_is_admin': (uuid in state.roomsFile[room]['admins'], None)
    }
    data = errors.multiple_error_handle(possible_errors, state)
    if(data): return data[0]
 
    # Modify and Send
    modify_room(room, ('ADMIN'), state, uuid= uuid)          
    return (f'/r{room}',
            encode_payload( [state.uuid_user(response['sender'])], state.system_codes['member_admin'], f'/r{room}'), 
            state)