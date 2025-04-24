#Header
import json
from message.catch_error import CatchError

errors = CatchError()

def new_room_member_setup(room:str, clientSock:object, state:object) -> object:
    #R emove Invite Remove
    state.room_invites[room].remove(clientSock)

    # Dictionary of Room and its Reverse
    state.room_socks[room].append(clientSock)
    state.sock_rooms[clientSock] = room

    # Data Added to Files (Rooms & Accounts)
    state.roomsFile[room]['members'].append(state.sock_uuid[clientSock])
    state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room)

    return state

def room_handle(clientSock:object, response:dict, state:object) -> tuple:
    room = response['receiver'][2::]

    #Catch Errors
    possible_errors = {
        "er_Invalid_room": room not in state.room_socks,
        "not_room_member": not(clientSock in state.room_socks[room] or clientSock in state.room_invites[room])
    }

    data = errors.multiple_error_handle(possible_errors, state)
    if(data): return data[0]

    #Prepare message to be sent
    response.pop('receiver') 
    username = state.uuid_user(response['sender'])
    response['sender'] = f"[{room}] {username}"
            
    # If New Member
    if(clientSock in state.room_invites[room]):
        state = new_room_member_setup(room, clientSock, state)
        response['sender'] = f"New Member! {username} Joined\n{response['sender']}"

    return (f'/r{room}', json.dumps(response), state)


def dm_handle(response:dict, state:object) -> tuple:
    #Sender: UUID->USERNAME  ; Receiver: USERNAME->UUID
    response['sender'] = state.uuid_user(response['sender'])    
    receiver = state.uuidsFile[response.pop('receiver')]

    return (receiver, json.dumps(response), state)
