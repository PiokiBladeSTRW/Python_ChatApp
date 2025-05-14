'''
Functions to be Utilized for Room Subcommands. 
<> Wraps indicate the Function is used only within this very Module
'''

#Header
from session_state import state
import commands.error_handle as errors

'''----------------------------------------------'''

'''Join a Room'''
def join_room(room_name:str) -> tuple:    
    state.log(f"Running room:join {room_name}")

    uuid = state.name_uuid(room_name)
    if(uuid == 0): return (None, None)
    state.receiver_id_change(uuid)

    payload = ((state.client_codes['room_join'], ''), state.msgTypes['system'])
    return ('ws_send', payload)  

'''Create a Room'''
def create_room(room_name:str) -> tuple: 
    state.log(f"Running room:create {room_name}") 
    
    payload = ((state.client_codes['room_create'], [room_name]), state.msgTypes['system'])
    return ('ws_send', payload)

'''Invite user to Room'''
def invite_user(username:str) -> tuple:  
    state.log(f"Running room:invite {username}")      

    uuid = state.name_uuid(username)
    if(uuid == 0): return (None, None)    
    
    payload = ((state.client_codes['room_invite'],  uuid), state.msgTypes['system'])
    return ('ws_send', payload)

'''Make user an Admin'''
def admin_user(username:str) -> tuple:
    state.log(f"Running room:adming {username}")    

    uuid = state.name_uuid(username)
    if(uuid == 0): return (None, None)
    
    payload = ((state.client_codes['room_admin'], uuid), state.msgTypes['system'])
    return ('ws_send', payload)

'''Kick User from Room'''
def kick_user(username:str) -> tuple:
    state.log(f"Running room:kick {username}")    

    uuid = state.name_uuid(username)
    if(uuid == 0): return (None, None)
    
    payload = ( (state.client_codes['room_kick'], uuid), state.msgTypes['system'])
    return ('ws_send', payload)

'''Ban User from Room'''
def ban_user(username:str) -> tuple:
    state.log(f"Running room:ban {username}")    

    uuid = state.name_uuid(username)
    if(uuid == 0): return (None, None)
    
    payload = ( (state.client_codes['room_ban'], uuid), state.msgTypes['system'])
    return ('ws_send', payload)

'''Unban User from Room'''
def unban_user(username: str) -> tuple:
    state.log(f"Running room:unban {username}")    

    uuid = state.name_uuid(username)
    if(uuid == 0): return (None, None)

    payload = ( (state.client_codes['room_unban'], uuid), state.msgTypes['system'])
    return ('ws_send', payload)


'''Members in Room'''  
def members() -> tuple: 
    state.log(f"Running room:members")   
    return ('ap_get', ('room_members', state.receiver_id))

'''Obtain Info of Room'''
def info() -> tuple:
    state.log(f"Running room:info")
    return ('ap_get', ('room_info', state.receiver_id))

'''Set Room Description'''
def set_desc(description: list) -> tuple:
    state.log(f"Running room:desc {description}")

    description = ' '.join(description)
    return ('ap_post', ('room_desc', description))