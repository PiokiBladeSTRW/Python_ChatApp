#Header
import json
from server_state import state
from message.catch_error import CatchError

errors = CatchError()

'''----------------------------------------------'''

def room_handle(response:dict) -> tuple:
    room = response['receiver'][2::]
    response.pop('receiver')    
    response['sender_id'] = (room, state.uuid_user(response['sender_id']))
    
    return (f'/r{room}', json.dumps(response))

'''----------------------------------------------'''


def dm_handle(response:dict) -> tuple: 

    # Handle Errors
    possible_errors = {
        'er_Invalid_user':  (response['receiver'] not in state.uuidsFile, [response['receiver']]),
        'user_exit':        (state.user_uuid(response['receiver']) not in state.uuid_sock, [response['receiver']])
    }
    
    if(data := errors.multiple_error_handle(possible_errors)): return data

    #sender_id: UUID->USERNAME  ; Receiver: USERNAME->UUID
    response['sender_id'] = state.uuid_user(response['sender_id'])    
    receiver = state.user_uuid(response.pop('receiver'))

    return (receiver, json.dumps(response))
