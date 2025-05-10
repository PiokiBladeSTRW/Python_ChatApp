# Header
import json
import time
import uuid
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

def encode_payload(command:int=None, content=None,  sender_id: str = None) -> str:
    data = {
        'command': command,
        'content': content,
        'type': 'sys',
    }
    if(sender_id): data['sender_id'] = sender_id
    return json.dumps(data)

def modify_room(room_uuid:str, operation: tuple, clientSock:object =None, user_uuid:str =None, room_name: str = None):
    '''Types of Operation: (CREATE, N_JOIN, INVITE, R_INVITE, ADMIN, KICK, BAN)
    clientSock: Person using Command ;  uuid: Person on receiving End of Command
    Returning Operations: (CREATE,)'''    

    # Ran By Person Creating Server
    if('CREATE' in operation):        
        room_uuid = 'room_' + str(uuid.uuid4())

        state.room_sock[room_uuid] = []
        state.roomName_roomUuid[room_name] = room_uuid
        state.roomsFile[room_uuid] = {'name': room_name,
                                      'members': [], 
                                      'admins': [], 
                                      'invites': [], 
                                      'bans': [],
                                      'creation': time.strftime("%D", time.localtime()),
                                      'desc': ""}          
        return room_uuid

    # Ran by Person joining Server
    if('N_JOIN' in operation):
        state.room_sock[room_uuid].append(clientSock)
        state.sock_rooms[clientSock].append(room_uuid)       

        state.roomsFile[room_uuid]['members'].append(state.sock_uuid[clientSock])
        state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room_uuid)      
    
    # Ran by Admin Targetted to Invitee
    if('INVITE' in operation):
        state.roomsFile[room_uuid]['invites'].append(user_uuid)  

    # Ran by Person joining Server
    if('R_INVITE' in operation):
        state.roomsFile[room_uuid]['invites'].remove(state.sock_uuid[clientSock])

    # Ran by Admin Targetted to Member
    if('ADMIN' in operation):
        state.roomsFile[room_uuid]['admins'].append(user_uuid)

    # Ran by Admin Targetted to Member
    if('KICK' in operation):
        state.roomsFile[room_uuid]['members'].remove(user_uuid)
        state.accountsFile[user_uuid]['rooms'].remove(room_uuid)

        state.sock_rooms[state.uuid_sock[user_uuid]].remove(room_uuid)
        state.room_sock[room_uuid].remove(state.uuid_sock[user_uuid])
    
    # Ran by Admin Targetted to Member
    if('BAN' in operation):
        state.roomsFile[room_uuid]['bans'].append(user_uuid)
    
    # Ran by Admin Targetted to Member
    if('UNBAN' in operation):            
        state.roomsFile[room_uuid]['bans'].remove(user_uuid)   


'''----------------------------------------------'''


'''# Lets user close safely [/exit]'''
def user_exit() -> tuple:
    return ('*', '/exit')

'''# Gives user a list of online members [/online]'''
def online_list(response:dict) -> tuple:
    uuid_data = list(state.uuid_sock)
    uuid_data.remove(response['sender_id'])
    
    user_data = [state.uuid_user(x) for x in uuid_data]
    data = '\n'.join(user_data)    

    return ('/s', encode_payload(content= data))

'''# Gives user a list of rooms [/rooms]'''
def room_list() -> tuple:
    data = '\n'.join(state.roomName_roomUuid)
    return ('/s', encode_payload(content= data))

'''# Gives user a list of room members [/room members]'''
def room_members(response: dict) -> tuple:    
    member_data = '\n'.join([state.uuid_user(x) for x in state.roomsFile[response['receiver_id']]['members']])
    return ('/s', encode_payload(content = member_data))

'''# Gives user a detailed info on room [/room info]'''
def room_info(response:dict) -> tuple:
    room = response['receiver_id']

    desc, created = state.roomsFile[room]['desc'], state.roomsFile[room]['creation']
    info_data = f"\nRoom Name: {room} \nDescription: {desc} \nCreated On: {created}"
    return ('/s', encode_payload(content=info_data))

'''# Sets Room's Description [/room desc]'''
def room_desc(response:dict) -> tuple:
    room_uuid = response['receiver_id']

    if(data := errors.error_handle(response['sender_id'] not in state.roomsFile[room_uuid]['admins'], 'er_Not_admin')): 
        return data

    state.roomsFile[room_uuid]['desc'] = response['content']
    return ('*', None)  

'''# Gives user the profile of Asked Individual [/profile get]'''
def profile_get(response:dict) -> tuple:    
    user_uuid  = response['content']

    if(data := errors.error_handle(user_uuid not in state.accountsFile, 'er_Invalid_user')): return data

    profile = state.uuidsFile[user_uuid]['profile']   
    
    data = f"{user_uuid}> {profile}"
    return ('/s', encode_payload(content= data))

'''# Allows user to modify their profile [/profile set]'''
def profile_set(response:dict) -> tuple:
    profile = response['content']
    state.uuidsFile[state.uuid_user(response['sender_id'])]['profile'] = profile

    return('*', None)   

'''============================='''


'''# Join a Room [/room join]'''
def room_join(clientSock:object, response:dict) -> tuple:    
    room_uuid = response['receiver_id']

    #ERROR HANDLING [NOT DONE BY ERROR CLASS DUE TO SECOND CONDITION BEING MASSING AND DEPENDENT ON FIRST]
    if(data := errors.error_handle(room_uuid not in state.roomsFile, 'er_Invalid_room')): return data

    if(not(clientSock in state.room_sock[room_uuid] or state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites'])): 
        return ('/s', encode_payload(state.system_codes['er_Not_room_member']))  
    
    if(state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites']): 
        modify_room(room_uuid, ('N_JOIN', 'R_INVITE'), clientSock)    
        return (room_uuid, encode_payload(state.system_codes['new_room_member'],
                [response['sender_id']], room_uuid))
    else:         
        return ('*', None)  


'''# Creates a new room [/room create]'''
def room_create(clientSock:object, response:dict) -> tuple:
    room_name = response['content'][0]

    room_uuid = modify_room(None, ('CREATE',), clientSock, room_name=room_name)

    modify_room(room_uuid, ('N_JOIN', 'ADMIN'), clientSock, state.sock_uuid[clientSock])    

    return ('/s', encode_payload(state.system_codes['room_live'], sender_id= room_uuid))

'''# Invites someone to a room [/room invite]'''
def room_invite(response:dict) -> tuple:    
    room_uuid, user_uuid = response['receiver_id'], response['content']

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (user_uuid not in state.accountsFile, [user_uuid]),
        'user_exit':        (user_uuid not in state.uuid_sock, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_in_room':(
            state.uuid_sock.get(user_uuid) in state.room_sock[room_uuid] or 
            user_uuid in state.roomsFile[room_uuid]['invites'], None),
        'member_ban' :       (user_uuid in state.roomsFile[room_uuid]['bans'], [room_uuid, user_uuid])
    }
    
    if(data := errors.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send      
    modify_room(room_uuid, ('INVITE',), user_uuid= user_uuid)
    return (user_uuid, encode_payload(state.system_codes['room_invite'], sender_id= room_uuid))

'''# Makes someone an Admin of Room [/room admin]'''
def room_admin(response:dict) -> tuple:    
    room_uuid, user_uuid = response['receiver_id'], response['content']

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (user_uuid not in state.accountsFile, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_is_admin':(user_uuid in state.roomsFile[room_uuid]['admins'], None)
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data
 
    # Modify and Send
    modify_room(room_uuid, ('ADMIN',), user_uuid= user_uuid)          
    return (room_uuid,
            encode_payload( state.system_codes['member_admin'],[user_uuid], room_uuid))

'''# Kick someone from the Room [/room kick]'''
def room_kick(response:dict) -> tuple:
    room_uuid, user_uuid = response['receiver_id'], response['content'] 

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (user_uuid not in state.accountsFile, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Not_in_room':   (user_uuid not in state.roomsFile[room_uuid]['members'], None)
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    modify_room(room_uuid, ('KICK',), user_uuid= user_uuid)          
    return (
        (room_uuid, encode_payload( state.system_codes['member_kick'], [user_uuid], room_uuid)),
        (user_uuid, encode_payload( state.system_codes['got_kicked'], [user_uuid], room_uuid))
        )

'''# Ban someone from the Room [/room ban]'''
def room_ban(response:dict) -> tuple:
    room_uuid, user_uuid = response['receiver_id'], response['content']  

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (user_uuid not in state.accountsFile, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Not_in_room':   (user_uuid not in state.roomsFile[room_uuid]['members'], None),
        'member_ban' :       (user_uuid in state.roomsFile[room_uuid]['bans'], [room_uuid, user_uuid])
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    modify_room(room_uuid, ('BAN', 'KICK'), user_uuid= user_uuid)          
    return (
        (room_uuid, encode_payload( state.system_codes['member_ban'],  [user_uuid], room_uuid)),
        (user_uuid, encode_payload( state.system_codes['got_banned'], [user_uuid], room_uuid))
        )

'''# Unban someone from the Room [/room unban]'''
def room_unban(response:dict) -> tuple:    
    room_uuid, user_uuid = response['receiver_id'], response['content']  

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (user_uuid not in state.accountsFile, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_not_ban': (user_uuid not in state.roomsFile[room_uuid]['bans'], None)
    }
    if(data := errors.multiple_error_handle(possible_errors)): return data

    # Modify and Send
    modify_room(room_uuid, ('UNBAN',), user_uuid= user_uuid)          
    return (
        (room_uuid, encode_payload( state.system_codes['member_unban'],  [user_uuid], room_uuid))
        )