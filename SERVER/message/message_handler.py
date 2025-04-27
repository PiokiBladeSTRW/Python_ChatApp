#Header
import json
from message.catch_error import CatchError

errors = CatchError()

'''----------------------------------------------'''

def room_handle(clientSock:object, response:dict, state:object) -> tuple:
    room = response['receiver'][2::]
    possible_errors = {
        "not_room_member": not(clientSock in state.room_socks[room] or clientSock in state.roomsFile[room]['invites'])
    }
    data = errors.multiple_error_handle(possible_errors, state)
    if(data): return data[0]

    response.pop('receiver')
    response['sender'] = (room, state.uuid_user(response['sender']))
    return (f'/r{room}', json.dumps(response), state)

'''----------------------------------------------'''


def dm_handle(response:dict, state:object) -> tuple:

    #Ensure receiving username is valid
    if(state.uuid_user(response['receiver']) not in state.uuid_sock):
        return ('/s', json.dumps({"content": state.system_codes['user_exit'], "type":'sys'}))

    #Sender: UUID->USERNAME  ; Receiver: USERNAME->UUID
    response['sender'] = state.uuid_user(response['sender'])    
    receiver = state.uuidsFile[response.pop('receiver')]

    return (receiver, json.dumps(response), state)
