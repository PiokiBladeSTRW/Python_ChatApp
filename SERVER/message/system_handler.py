# Header
from server_state import state
from message.utilities import utility

'''
Commands and their Arguments:
1: Exit -> None
2: Online List -> None
3: Rooms List -> None
4: Create Room -> Room_Name
5: Room Invite -> (Room Name, Username)
6: Room Admin -> (Room Name, Username)'''


'''----------------------------------------------'''
'''# Lets user close safely [/exit]'''
def user_exit() -> tuple:
    return ('*', '/exit')


'''# Join a Room [/room join]'''
def room_join(clientSock:object, response:dict) -> tuple:    
    room_uuid = response['receiver_id']

    #ERROR HANDLING [NOT DONE BY ERROR CLASS DUE TO SECOND CONDITION BEING MASSING AND DEPENDENT ON FIRST]
    if(data := utility.error_handle(room_uuid not in state.roomsFile, 'er_Invalid_room')): return data

    if(not(clientSock in state.room_sock[room_uuid] or state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites'])): 
        return ('/s', utility.encode_payload(state.system_codes['er_Not_room_member']))  
    
    if(state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites']): 
        utility.modify_room(room_uuid, ('N_JOIN', 'R_INVITE'), clientSock)   
        members = [x for x in state.roomsFile[room_uuid]['members']].remove(response['sender_id'])
        return (
            (room_uuid, utility.encode_payload(state.system_codes['new_room_member'],[response['sender_id']], room_uuid)),
            ('/s', utility.encode_payload(state.system_codes['no_display'], members, room_uuid)))
    else:         
        return ('*', None)  


'''# Creates a new room [/room create]'''
def room_create(clientSock:object, response:dict) -> tuple:
    room_name = response['content'][0]

    room_uuid = utility.modify_room(None, ('CREATE',), clientSock, room_name=room_name)

    utility.modify_room(room_uuid, ('N_JOIN', 'ADMIN'), clientSock, state.sock_uuid[clientSock])    

    return ('/s', utility.encode_payload(state.system_codes['room_live'], sender_id= room_uuid))

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
    
    if(data := utility.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send      
    utility.modify_room(room_uuid, ('INVITE',), user_uuid= user_uuid)
    return (user_uuid, utility.encode_payload(state.system_codes['room_invite'], sender_id= room_uuid))

'''# Makes someone an Admin of Room [/room admin]'''
def room_admin(response:dict) -> tuple:    
    room_uuid, user_uuid = response['receiver_id'], response['content']

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (user_uuid not in state.accountsFile, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Member_is_admin':(user_uuid in state.roomsFile[room_uuid]['admins'], None)
    }
    if(data := utility.multiple_error_handle(possible_errors)): return data
 
    # Modify and Send
    utility.modify_room(room_uuid, ('ADMIN',), user_uuid= user_uuid)          
    return (room_uuid,
            utility.encode_payload( state.system_codes['member_admin'],[user_uuid], room_uuid))

'''# Kick someone from the Room [/room kick]'''
def room_kick(response:dict) -> tuple:
    room_uuid, user_uuid = response['receiver_id'], response['content'] 

    #Catch Errors
    possible_errors = {
        'er_Invalid_user':  (user_uuid not in state.accountsFile, [user_uuid]),
        'er_Not_admin':     (response['sender_id'] not in state.roomsFile[room_uuid]['admins'], None),
        'er_Not_in_room':   (user_uuid not in state.roomsFile[room_uuid]['members'], None)
    }
    if(data := utility.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    utility.modify_room(room_uuid, ('KICK',), user_uuid= user_uuid)          
    return (
        (room_uuid, utility.encode_payload( state.system_codes['member_kick'], [user_uuid], room_uuid)),
        (user_uuid, utility.encode_payload( state.system_codes['got_kicked'], [user_uuid], room_uuid))
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
    if(data := utility.multiple_error_handle(possible_errors)): return data
    
    # Modify and Send
    utility.modify_room(room_uuid, ('BAN', 'KICK'), user_uuid= user_uuid)          
    return (
        (room_uuid, utility.encode_payload( state.system_codes['member_ban'],  [user_uuid], room_uuid)),
        (user_uuid, utility.encode_payload( state.system_codes['got_banned'], [user_uuid], room_uuid))
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
    if(data := utility.multiple_error_handle(possible_errors)): return data

    # Modify and Send
    utility.modify_room(room_uuid, ('UNBAN',), user_uuid= user_uuid)          
    return (
        (room_uuid, utility.encode_payload( state.system_codes['member_unban'],  [user_uuid], room_uuid))
        )