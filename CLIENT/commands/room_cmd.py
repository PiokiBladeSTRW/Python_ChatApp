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
    state.receiver_change('/r'+room_name)
    payload = ((state.client_codes['room_join'], room_name), state.msgTypes['system'])
    return ('send', payload)    

'''Create a Room'''
def create_room(room_name:str) -> tuple: 
    state.log(f"Running room:create {room_name}")

    if(room_name in state.clientRoomsFile): return errors.error_handle("Room Already Exists")        

    state.clientRoomsFile.append(room_name)

    state.receiver_change('/r'+room_name)                
    payload = ((state.client_codes['room_create'], room_name), state.msgTypes['system'])
    return ('send', payload)

'''Invite user to Room'''
def invite_user(username:str) -> tuple:  
    state.log(f"Running room:invite {username}")  
    if(not state.receiver.startswith('/r')): return errors.error_handle("Invalid Room")

    room = state.receiver[2::]
    payload = ((state.client_codes['room_invite'],  (room,username)), state.msgTypes['system'])
    return ('send', payload)

'''Make user an Admin'''
def admin_user(username:str) -> tuple:
    state.log(f"Running room:adming {username}")
    if(not state.receiver.startswith('/r')): return errors.error_handle("Invalid Room")

    room = state.receiver[2::]
    payload = ((state.client_codes['room_admin'], (room,username)), state.msgTypes['system'])
    return ('send', payload)

'''Kick User from Room'''
def kick_user(username:str) -> tuple:
    state.log(f"Running room:kick {username}")
    if(not state.receiver.startswith('/r')): return errors.error_handle("Invalid Room")

    room = state.receiver[2::]
    payload = ( (state.client_codes['room_kick'], (room, username)), state.msgTypes['system'])
    return ('send', payload)

'''Ban User from Room'''
def ban_user(username:str) -> tuple:
    state.log(f"Running room:ban {username}")
    if(not state.receiver.startswith('/r')): return errors.error_handle("Invalid Room")

    room = state.receiver[2::]
    payload = ( (state.client_codes['room_ban'], (room, username)), state.msgTypes['system'])
    return ('send', payload)