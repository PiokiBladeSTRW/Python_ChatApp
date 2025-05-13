#Solo File handling API data Request Parsing & Responding
from message.utilities import utility
from server_state import state

'''# Lets user close safely [/exit]'''
def user_exit() -> tuple:
    return ('*', '/exit')

'''# Gives user a list of online members [/online]'''
def online_list(response:dict) -> tuple:
    uuid_data = list(state.uuid_sock)
    uuid_data.remove(response['sender_id'])
    
    user_data = [state.uuid_user(x) for x in uuid_data]
    data = '\n'.join(user_data)    

    return ('/s', utility.encode_payload(content= data))

'''# Gives user a list of rooms [/rooms]'''
def room_list() -> tuple:
    data = '\n'.join(state.roomName_roomUuid)
    return ('/s', utility.encode_payload(content= data))

'''# Gives user a list of room members [/room members]'''
def room_members(response: dict) -> tuple:    
    member_data = [x for x in state.roomsFile[response['receiver_id']]['members']]
    return ('/s', utility.encode_payload(state.system_codes['room_members'], member_data, response['receiver_id']))

'''# Gives user a detailed info on room [/room info]'''
def room_info(response:dict) -> tuple:
    room = response['receiver_id']

    desc, created = state.roomsFile[room]['desc'], state.roomsFile[room]['creation']
    info_data = f"\nRoom Name: {room} \nDescription: {desc} \nCreated On: {created}"
    return ('/s', utility.encode_payload(content=info_data))

'''# Sets Room's Description [/room desc]'''
def room_desc(response:dict) -> tuple:
    room_uuid = response['receiver_id']

    if(data := utility.error_handle(response['sender_id'] not in state.roomsFile[room_uuid]['admins'], 'er_Not_admin')): 
        return data

    state.roomsFile[room_uuid]['desc'] = response['content']
    return ('*', None)  

'''# Gives user the profile of Asked Individual [/profile get]'''
def profile_get(response:dict) -> tuple:    
    user_uuid  = response['content']

    if(data := utility.error_handle(user_uuid not in state.accountsFile, 'er_Invalid_user')): return data

    profile = state.uuidsFile[user_uuid]['profile']   
    
    data = f"{user_uuid}> {profile}"
    return ('/s', utility.encode_payload(content= data))

'''# Allows user to modify their profile [/profile set]'''
def profile_set(response:dict) -> tuple:
    profile = response['content']
    state.uuidsFile[state.uuid_user(response['sender_id'])]['profile'] = profile

    return('*', None)   

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