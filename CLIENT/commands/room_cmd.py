'''
Functions to be Utilized for Room Subcommands. 
<> Wraps indicate the Function is used only within this very Module
'''

#Header
import commands.error_handle as errors

'''----------------------------------------------'''

'''========================== type : msg'''


'''Join a Room'''
def join_room(args:list, state:object) -> tuple:     
    '''Args[0] = Room, Args[1::] = Message'''   
     
    state.receiver_change('/r'+args[0])
    payload = (' '.join(args[1::]), state.msgTypes['message'])
    return ('send', payload, state)    


'''========================== type : sys'''
   

'''Create a Room'''
def create_room(room_name:str, state:object) -> tuple:   
    state.receiver_change('/r'+room_name)                
    payload = ((state.client_codes['room_create'], room_name), state.msgTypes['system'])
    return ('send', payload, state)

'''Invite user to Room'''
def invite_user(username:str, state:object) -> tuple:    
    if(not state.receiver.startswith('/r')): return errors.error_handle("The Room does not Exist!", state)

    payload = ((state.client_codes['room_invite'],  username), state.msgTypes['system'])
    return ('send', payload, state)

'''Make user an Admin'''
def admin_user(username:str, state:object) -> tuple:
    if(not state.receiver.startswith('/r')): return errors.error_handle("The Room does not Exist!", state)

    payload = ((state.client_codes['room_admin'], username), state.msgTypes['system'])
    return ('send', payload, state)