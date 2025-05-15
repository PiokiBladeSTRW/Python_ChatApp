# Header
import json
import uuid
import time
from server_state import state
from message.catch_error import ErrorHandle

'''
Commands and their Arguments:
1: Exit -> None
2: Online List -> None
3: Rooms List -> None
4: Create Room -> Room_Name
5: Room Invite -> (Room Name, Username)
6: Room Admin -> (Room Name, Username)'''

error = ErrorHandle()

def encode_payload(command:int=None, content=None,  sender_id: str = None) -> str:
    data = {
        'command': command,
        'content': content,
        'type': 'sys',
    }
    if(sender_id): data['sender_id'] = sender_id
    return json.dumps(data)

def modify_room(room_uuid:str, operation: tuple, clientSock:object=None, user_uuid:str=None, room_name:str=None):
    '''Types of Operation: (CREATE, N_JOIN, INVITE, R_INVITE, ADMIN, KICK, BAN)
    clientSock: Person using Command ;  uuid: Person on receiving End of Command
    Returning Operations: (CREATE,)'''    

    # Ran By Person Creating Server
    if('CREATE' in operation):        
        room_uuid = 'room_' + str(uuid.uuid4())

        state.room_sock[room_uuid] = []
        state.roomName_roomUuid[room_name] = room_uuid
        state.roomsFile[room_uuid] = {'name': room_name,
                                    'owner': state.sock_uuid[clientSock],
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
        state.uuidsFile[state.sock_uuid[clientSock]]['rooms'].append(room_uuid)   

    # Ran by Person leaving Server
    if('LEAVE' in operation):
        state.room_sock[room_uuid].remove(clientSock)
        state.sock_rooms[clientSock].remove(room_uuid)

        state.roomsFile[room_uuid]['members'].remove(state.sock_uuid[clientSock])
        state.uuidsFile[state.sock_uuid[clientSock]]['rooms'].remove(room_uuid)
    
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
    if('DEMOTE' in operation):
        if(user_uuid in state.roomsFile[room_uuid]['admins']):
            state.roomsFile[room_uuid]['admins'].remove(user_uuid)

    # Ran by Admin Targetted to Member
    if('KICK' in operation):
        state.roomsFile[room_uuid]['members'].remove(user_uuid)
        state.uuidsFile[user_uuid]['rooms'].remove(room_uuid)

        state.sock_rooms[state.uuid_sock[user_uuid]].remove(room_uuid)
        state.room_sock[room_uuid].remove(state.uuid_sock[user_uuid])
    
    # Ran by Admin Targetted to Member
    if('BAN' in operation):
        state.roomsFile[room_uuid]['bans'].append(user_uuid)
    
    # Ran by Admin Targetted to Member
    if('UNBAN' in operation):            
        state.roomsFile[room_uuid]['bans'].remove(user_uuid)  

    # Ran by OWNER Targetted to Member
    if('TRANSFER' in operation):
        state.roomsFile[room_uuid]['owner'] = user_uuid


'''----------------------------------------------'''
'''# Lets user close safely [/exit]'''
def user_exit() -> tuple:
    return ('*', '/exit')


'''# Join a Room [/room join]'''
def room_join(clientSock:object, response:dict) -> tuple:    
    room_uuid = response['receiver_id']

    #ERROR HANDLING [NOT DONE BY ERROR CLASS DUE TO SECOND CONDITION BEING MASSING AND DEPENDENT ON FIRST]
    if(data := error.error_handle(room_uuid not in state.roomsFile, 'er_Invalid_room')): return data

    if(not(clientSock in state.room_sock[room_uuid] or state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites'])): 
        return ('/s', encode_payload(state.system_codes['er_Not_room_member']))  
    
    if(state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites']): 
        modify_room(room_uuid, ('N_JOIN', 'R_INVITE'), clientSock)   
        members = [x for x in state.roomsFile[room_uuid]['members']].remove(response['sender_id'])
        return (
            (room_uuid, encode_payload(state.system_codes['new_room_member'],[response['sender_id']], room_uuid)),
            ('/s', encode_payload(state.system_codes['no_display'], members, room_uuid)))
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
        'user_exit':        (user_uuid not in state.uuid_sock, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_in_room':(
            state.uuid_sock.get(user_uuid) in state.room_sock[room_uuid] or 
            user_uuid in state.roomsFile[room_uuid]['invites'], None),
        'member_ban' :       (user_uuid in state.roomsFile[room_uuid]['bans'], [room_uuid, user_uuid])
    }
    
    if(data := error.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send      
    modify_room(room_uuid, ('INVITE',), user_uuid= user_uuid)
    return (user_uuid, encode_payload(state.system_codes['room_invite'], sender_id= room_uuid))

'''# Makes someone an Admin of Room [/room admin]'''
def room_admin(response:dict) -> tuple:    
    room_uuid, user_uuid = response['receiver_id'], response['content']

    #Catch Errors
    possible_errors = {        
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_is_admin':(user_uuid in state.roomsFile[room_uuid]['admins'], None)
    }
    if(data := error.multiple_error_handle(possible_errors)): return data
 
    # Modify and Send
    modify_room(room_uuid, ('ADMIN',), user_uuid= user_uuid)          
    return (room_uuid,
            encode_payload( state.system_codes['member_admin'],[user_uuid], room_uuid))

'''# Makes someone no longer Admin of Room [/room demote]'''
def room_demote(response:dict) -> tuple:    
    room_uuid, user_uuid = response['receiver_id'], response['content']

    #Catch Errors
    possible_errors = {        
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_not_admin':(user_uuid not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_owner': (user_uuid == state.roomsFile[room_uuid]['owner'], None)
    }
    if(data := error.multiple_error_handle(possible_errors)): return data
 
    # Modify and Send
    modify_room(room_uuid, ('DEMOTE',), user_uuid= user_uuid)          
    return (room_uuid,
            encode_payload( state.system_codes['member_demote'],[user_uuid], room_uuid))

'''# Kick someone from the Room [/room kick]'''
def room_kick(response:dict) -> tuple:
    room_uuid, user_uuid = response['receiver_id'], response['content'] 

    #Catch Errors
    possible_errors = {        
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Not_in_room':   (user_uuid not in state.roomsFile[room_uuid]['members'], None),
        'er_Member_owner': (user_uuid == state.roomsFile[room_uuid]['owner'], None)
    }
    if(data := error.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    modify_room(room_uuid, ('KICK', 'DEMOTE'), user_uuid= user_uuid)          
    return (
        (room_uuid, encode_payload( state.system_codes['member_kick'], [user_uuid], room_uuid)),
        (user_uuid, encode_payload( state.system_codes['got_kicked'], [user_uuid], room_uuid))
        )

'''# Ban someone from the Room [/room ban]'''
def room_ban(response:dict) -> tuple:
    room_uuid, user_uuid = response['receiver_id'], response['content']  

    #Catch Errors
    possible_errors = {        
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Not_in_room':   (user_uuid not in state.roomsFile[room_uuid]['members'], None),
        'member_ban' :       (user_uuid in state.roomsFile[room_uuid]['bans'], [room_uuid, user_uuid]),
        'er_Member_owner': (user_uuid == state.roomsFile[room_uuid]['owner'], None)
    }
    if(data := error.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    modify_room(room_uuid, ('BAN', 'KICK', 'DEMOTE'), user_uuid= user_uuid)          
    return (
        (room_uuid, encode_payload( state.system_codes['member_ban'],  [user_uuid], room_uuid)),
        (user_uuid, encode_payload( state.system_codes['got_banned'], [user_uuid], room_uuid))
        )

'''# Unban someone from the Room [/room unban]'''
def room_unban(response:dict) -> tuple:    
    room_uuid, user_uuid = response['receiver_id'], response['content']  

    #Catch Errors
    possible_errors = {        
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_not_ban': (user_uuid not in state.roomsFile[room_uuid]['bans'], None)
    }
    if(data := error.multiple_error_handle(possible_errors)): return data

    # Modify and Send
    modify_room(room_uuid, ('UNBAN',), user_uuid= user_uuid)          
    return (
        (room_uuid, encode_payload( state.system_codes['member_unban'],  [user_uuid], room_uuid))
        )

'''# Makes someone the Owner of Room [/room transfer]'''
def transfer(response:dict) -> tuple:    
    # !!! NEEDS A CONFIRMATION MENU LATER !!!
    room_uuid, user_uuid = response['receiver_id'], response['content']

    #Catch Errors
    possible_errors = {        
        'er_Not_owner':     (response['sender_id'] != state.roomsFile[room_uuid]['owner'], None)
    }
    if(data := error.multiple_error_handle(possible_errors)): return data
 
    # Modify and Send
    modify_room(room_uuid, ('TRANSFER',), user_uuid= user_uuid)          
    return (room_uuid,
            encode_payload( state.system_codes['new_owner'],[user_uuid], room_uuid))

'''# Leave a Room [/room leave]'''
def room_leave(clientSock:object, response:dict) -> tuple:    
    room_uuid = response['receiver_id']  

    if(data:= error.error_handle(response['sender'] == state.roomsFile[room_uuid]['owner'], 'member_owner')): return data

    modify_room(room_uuid, ('LEAVE', 'DEMOTE'), clientSock)
    
    return (room_uuid, encode_payload( state.system_codes['member_left'], [response['sender_id']], room_uuid))  