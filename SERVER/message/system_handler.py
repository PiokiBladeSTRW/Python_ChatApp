# Header
import json
from server_state import state
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

def encode_payload(command:int=None, content=None,  sender: str = None) -> str:
    data = {
        'command': command,
        'content': content,
        'type': 'sys',
    }
    if(sender): data['sender'] = sender
    return json.dumps(data)

def modify_room(room:str, operation: tuple, clientSock:object =None, uuid:str =None ) -> None:
    '''Types of Operation: (CREATE, N_JOIN, INVITE, R_INVITE, ADMIN, KICK, BAN)
    clientSock: Person using Command ;  uuid: Person on receiving End of Command'''    

    # Ran By Person Creating Server
    if('CREATE' in operation):
        state.room_sock[room] = []
        state.roomsFile[room] = {'members': [], 'admins': [], 'invites': [], 'bans': []}  

    # Ran by Person joining Server
    if('N_JOIN' in operation):
        state.room_sock[room].append(clientSock)
        state.sock_rooms[clientSock].append(room)       

        state.roomsFile[room]['members'].append(state.sock_uuid[clientSock])
        state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room)      
    
    # Ran by Admin Targetted to Invitee
    if('INVITE' in operation):
        state.roomsFile[room]['invites'].append(uuid)  

    # Ran by Person joining Server
    if('R_INVITE' in operation):
        state.roomsFile[room]['invites'].remove(state.sock_uuid[clientSock])

    # Ran by Admin Targetted to Member
    if('ADMIN' in operation):
        state.roomsFile[room]['admins'].append(uuid)

    # Ran by Admin Targetted to Member
    if('KICK' in operation):
        state.roomsFile[room]['members'].remove(uuid)
        state.accountsFile[uuid]['rooms'].remove(room)

        state.sock_rooms[state.uuid_sock[uuid]].remove(room)
        state.room_sock[room].remove(state.uuid_sock[uuid])
    
    # Ran by Admin Targetted to Member
    if('BAN' in operation):
        state.roomsFile[room]['bans'].append(uuid)
    
    # Ran by Admin Targetted to Member
    if('UNBAN' in operation):            
        state.roomsFile[room]['bans'].remove(uuid)        


'''----------------------------------------------'''


'''# Lets user close safely [/exit]'''
def user_exit() -> tuple:
    return ('*', '/exit')

'''# Gives user a list of online members [/online]'''
def online_list(response:dict) -> tuple:
    uuid_data = list(state.uuid_sock)
    uuid_data.remove(response['sender'])
    
    user_data = [state.uuid_user(x) for x in uuid_data]
    data = '\n'.join(user_data)    

    return ('/s', encode_payload(content= data))

'''# Gives user a list of rooms [/rooms]'''
def room_list() -> tuple:
    data = '\n'.join(state.room_sock.keys())
    return ('/s', encode_payload(content= data))

'''# Gives user a list of room members [/room members]'''
def room_members(response: dict) -> tuple:    
    member_data = '\n'.join([state.uuid_user(x) for x in state.roomsFile[response['receiver']]['members']])
    return ('/s', encode_payload(content = member_data))

'''# Gives user the profile of Asked Individual'''
def profile_get(response:dict) -> tuple:    
    username  = response['content']

    if(data := errors.error_handle(username not in state.uuidsFile, 'er_Invalid_user')): return data

    profile = state.uuidsFile[username]['profile']   
    
    data = f"{username}> {profile}"
    return ('/s', encode_payload(content= data))

'''# Allows user to modify their profile'''
def profile_set(response:dict) -> tuple:
    profile = ' '.join(response['content'])
    state.uuidsFile[state.uuid_user(response['sender'])]['profile'] = profile

    return('*', None)   


'''============================='''


'''# Join a Room [/room join]'''
def room_join(clientSock:object, response:dict) -> tuple:
    room = response['receiver'][2::]

    #ERROR HANDLING [NOT DONE BY ERROR CLASS DUE TO SECOND CONDITION BEING MASSING AND DEPENDENT ON FIRST]
    if(data := errors.error_handle(room not in state.roomsFile, 'er_Invalid_room')): return data

    if(not(clientSock in state.room_sock[room] or state.sock_uuid[clientSock] in state.roomsFile[room]['invites'])): 
        return ('/s', encode_payload(state.system_codes['er_Not_room_member']))  
    
    if(state.sock_uuid[clientSock] in state.roomsFile[room]['invites']): 
        modify_room(room, ('N_JOIN', 'R_INVITE'), clientSock)    
        return (f'/r{room}', 
            encode_payload(state.system_codes['new_room_member'], [state.uuid_user(response['sender'])], f'/r{room}'))
    else:         
        return ('*', None)  


'''# Creates a new room [/room create]'''
def room_create(clientSock:object, response:dict) -> tuple:
    room = response['receiver'][2::]
    
    if(data := errors.error_handle(room in state.roomsFile, 'er_Room_exists')): return data
    
    modify_room(room, ('CREATE', 'N_JOIN', 'ADMIN'), clientSock, state.sock_uuid[clientSock])

    return ('/s', encode_payload(state.system_codes['room_live'], sender= f'/r{room}'))

'''# Invites someone to a room [/room invite]'''
def room_invite(response:dict) -> tuple:    
    room, username = response['receiver'][2::], response['content']

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (username not in state.uuidsFile, [username]),
        'user_exit':        (state.user_uuid(username) not in state.uuid_sock, [username]),
        'er_Not_admin':     (response['sender'] not in state.roomsFile[room]['admins'], None),
        'er_Member_in_room':(
            state.uuid_sock.get(state.user_uuid(username)) in state.room_sock[room] or 
            state.uuidsFile.get(username) in state.roomsFile[room]['invites'], None),
        'member_ban' :       (state.user_uuid(username) in state.roomsFile[room]['bans'], [room, username])
    }
    
    if(data := errors.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send  
    uuid = state.user_uuid(username)
    modify_room(room, ('INVITE',), uuid= uuid)
    return (uuid, encode_payload(state.system_codes['room_invite'], sender= f'/r{room}'))

'''# Makes someone an Admin of Room [/room admin]'''
def room_admin(response:dict) -> tuple:    
    room, username = response['receiver'][2::], response['content']

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (username not in state.uuidsFile, [username]),
        'er_Not_admin':     (response['sender'] not in state.roomsFile[room]['admins'], None),
        'er_Member_is_admin':(state.user_uuid(username) in state.roomsFile[room]['admins'], None)
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data
 
    # Modify and Send
    uuid = state.user_uuid(username)
    modify_room(room, ('ADMIN',), uuid= uuid)          
    return (f'/r{room}',
            encode_payload( state.system_codes['member_admin'],[username], f'/r{room}'))

'''# Kick someone from the Room [/room kick]'''
def room_kick(response:dict) -> tuple:
    room, username = response['receiver'][2::], response['content'] 

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (username not in state.uuidsFile, [username]),
        'er_Not_admin':     (response['sender'] not in state.roomsFile[room]['admins'], None),
        'er_Not_in_room':   (state.user_uuid(username) not in state.roomsFile[room]['members'], None)
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    uuid = state.user_uuid(username)
    modify_room(room, ('KICK',), uuid= uuid)          
    return (
        (f'/r{room}', encode_payload( state.system_codes['member_kick'], [username], f'/r{room}')),
        (uuid, encode_payload( state.system_codes['got_kicked'], [username], f'/r{room}'))
        )

'''# Ban someone from the Room [/room ban]'''
def room_ban(response:dict) -> tuple:
    room, username = response['receiver'][2::], response['content']  

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (username not in state.uuidsFile, [username]),
        'er_Not_admin':     (response['sender'] not in state.roomsFile[room]['admins'], None),
        'er_Not_in_room':   (state.user_uuid(username) not in state.roomsFile[room]['members'], None),
        'member_ban' :       (state.uuidsFile.get(username) in state.roomsFile[room]['bans'], [room, username])
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    uuid = state.user_uuid(username)
    modify_room(room, ('BAN', 'KICK'), uuid= uuid)          
    return (
        (f'/r{room}', encode_payload( state.system_codes['member_ban'],  [username], f'/r{room}')),
        (uuid, encode_payload( state.system_codes['got_banned'], [username], f'/r{room}'))
        )

'''# Unban someone from the Room [/room unban]'''
def room_unban(response:dict) -> tuple:    
    room, username = response['receiver'][2::], response['content']  

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (username not in state.uuidsFile, [username]),
        'er_Not_admin':     (response['sender'] not in state.roomsFile[room]['admins'], None),
        'er_Member_not_ban': (state.uuidsFile.get(username) not in state.roomsFile[room]['bans'], None)
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data

    # Modify and Send
    uuid = state.user_uuid(username) 
    modify_room(room, ('UNBAN',), uuid= uuid)          
    return (
        (f'/r{room}', encode_payload( state.system_codes['member_unban'],  [username], f'/r{room}'))
        )