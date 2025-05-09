#Header
import json
from server_state import state
from message.catch_error import CatchError

errors = CatchError()

'''----------------------------------------------'''

def room_handle(response:dict) -> tuple:
    room_uuid = response['receiver']
    response.pop('receiver')    
    response['sender_id'] = (room_uuid, response['sender_id'])
    
    return (room_uuid, json.dumps(response))

'''----------------------------------------------'''


def dm_handle(response:dict) -> tuple: 

    # Handle Errors
    possible_errors = {
        'er_Invalid_user':  (response['receiver'] not in state.accountsFile, [response['receiver']]),
        'user_exit':        (response['receiver'] not in state.uuid_sock, [response['receiver']])
    }
    
    if(data := errors.multiple_error_handle(possible_errors)): return data

    #sender_id: UUID->USERNAME  ; Receiver: USERNAME->UUID       
    receiver = response.pop('receiver')

    return (receiver, json.dumps(response))
