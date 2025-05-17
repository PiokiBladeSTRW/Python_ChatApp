#Header
import json
from server_state import state
from message.catch_error import ErrorHandle

error = ErrorHandle()

'''----------------------------------------------'''

def room_handle(response:dict) -> tuple:
    '''Handle Messages sent to Rooms'''

    room_uuid = response.pop('receiver_id')        
    response['sender_id'] = (room_uuid, response['sender_id'])
    
    return (room_uuid, json.dumps(response))

'''----------------------------------------------'''


def dm_handle(response:dict) -> tuple: 
    '''Handle Messages sent Directly'''

    # Handle Errors
    if(data := error.error_handle(response['receiver_id'] not in state.uuid_sock, 'user_exit',[response['receiver_id']])):
        return data

    receiver_id = response.pop('receiver_id')
    return (receiver_id, json.dumps(response))
