'''
Functions to be Utilized for Room Subcommands. 
<> Wraps indicate the Function is used only within this very Module
'''

#Header
import commands.error_handle as errors

'''----------------------------------------------'''

'''Join a Room'''
def join_room(room_name:str, state:object) -> tuple:    
    if(room_name in state.clientRoomsFile): 
        state.receiver_change('/r'+room_name)
        return (None, None, state)
    
    state.receiver_change('/r'+room_name)
    payload = ((state.client_codes['room_join'], room_name), state.msgTypes['system'])
    return ('send', payload, state)    

'''Create a Room'''
def create_room(room_name:str, state:object) -> tuple: 
    if(room_name in state.clientRoomsFile): return errors.error_handle("Room Already Exists", state)

    state.clientRoomsFile.append(room_name)

    state.receiver_change('/r'+room_name)                
    payload = ((state.client_codes['room_create'], room_name), state.msgTypes['system'])
    return ('send', payload, state)

'''Invite user to Room'''
def invite_user(username:str, state:object) -> tuple:    
    if(not state.receiver.startswith('/r')): return errors.error_handle("Invalid Room", state)

    room = state.receiver[2::]
    payload = ((state.client_codes['room_invite'],  (room,username)), state.msgTypes['system'])
    return ('send', payload, state)

'''Make user an Admin'''
def admin_user(username:str, state:object) -> tuple:
    if(not state.receiver.startswith('/r')): return errors.error_handle("Invalid Room", state)

    room = state.receiver[2::]
    payload = ((state.client_codes['room_admin'], (room,username)), state.msgTypes['system'])
    return ('send', payload, state)