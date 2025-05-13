#Header
import json
from server_state import state
from message.catch_error import CatchError

errors = CatchError()

'''----------------------------------------------'''

def room_handle(response:dict) -> tuple:
    room_uuid = response.pop('receiver_id')        
    response['sender_id'] = (room_uuid, response['sender_id'])
    
    return (room_uuid, json.dumps(response))

'''----------------------------------------------'''


def dm_handle(response:dict) -> tuple: 

    # Handle Errors
    possible_errors = {
        'er_Invalid_user':  (response['receiver_id'] not in state.accountsFile, [response['receiver_id']]),
        'user_exit':        (response['receiver_id'] not in state.uuid_sock, [response['receiver_id']])
    }
    
    if(data := errors.multiple_error_handle(possible_errors)): return data

    #sender_id: UUID->USERNAME  ; receiver_id: USERNAME->UUID       
    receiver_id = response.pop('receiver_id')

    return (receiver_id, json.dumps(response))
