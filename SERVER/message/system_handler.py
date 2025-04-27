# Header
import json
from message.catch_error import CatchError

errors = CatchError()
'''
Commands and their Arguments:
1: Exit -> None
2: Online List -> None
3: Rooms List -> None
4: Create Room -> Room_Name
5: Room Invite -> (Room Name, Username)
6: Room Admin -> (Room Name, Username)'''

# Lets user close safely [/exit]
def user_exit(state:object) -> tuple:
    return ('*', '/exit', state)

# Gives user a list of online members [/online]
def online_list(response:dict, state:object) -> tuple:
    uuid_data = list(state.uuid_sock)
    uuid_data.remove(response['sender'])

    user_data = (state.uuid_user(x) for x in uuid_data) 
    data = '\n'.join(user_data)    
    return ('/s', json.dumps({'content': data, 'type': 'sys'}), state)

# Gives user a list of rooms [/rooms]
def room_list(state:object) -> tuple:
    data = '\n'.join(state.room_socks.keys())
    return ('/s', json.dumps({'content': data, 'type': 'sys'}), state)

# Creates a new room [/room create]
def room_create(clientSock:object, response:dict, state:object) -> tuple:
    room = response['content']

    state.room_invites[room] = []        
    state.room_socks[room] = [clientSock]
    
    state.sock_rooms[clientSock].append(room)
    
    state.roomsFile[room] = {'members': [], 'admins': []}
    state.roomsFile[room]['members'].append(response['sender'])
    state.roomsFile[room]['admins'].append(response['sender'])

    state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room)

    return ('/s', json.dumps({'content': f"Room {room} Is LIVE", 'type': "sys"}), state)

# Invites someone to a room [/room invite]
def room_invite(response:dict, state:object) -> tuple:
    room, username = response['content'][0], response['content'][1]

    #Handle non-existent account, for now Offline
    if(username not in state.uuidsFile):
        return ('/s', json.dumps({'sender': username, 'content': state.system_codes['user_exit'], 'type': "sys"}), state)
    uuid = state.uuidsFile[username]

    #Catch Errors
    possible_errors = {
        'er_Invalid_room': room not in state.room_socks,
        'user_exit': uuid not in state.uuid_sock,
        'er_Not_admin': response['sender'] not in state.roomsFile[room]['admins']
    }
    data = errors.multiple_error_handle(possible_errors, state)
    if(data): return data[0]

    #If user is already in room OR already invite
    if(state.uuid_sock[uuid] in state.room_socks[room] or state.uuid_sock[uuid] in state.room_invites[room]):
        payload = json.dumps({"content": f"{username} already in {room}", "type":"sys"})

    else:        
        state.room_invites[room].append(state.uuid_sock[uuid])
        payload = json.dumps({"content": f"{room} has sent an Invitation", "type":"sys"})            
        return (uuid, payload, state)

# Makes someone an Admin of Room [/room admin]
def room_admin(response:dict, state:object) -> tuple:
    room, username = response['content'][0], response['content'][1] 

    #Handle non-existent account, for now Offline
    if(username not in state.uuidsFile):
        return ('/s', json.dumps({'sender': username, 'content': state.system_codes['user_exit'], 'type': "sys"}), state)  
    uuid = state.uuidsFile[username]       

    #Catch Errors
    possible_errors = {
        'er_Invalid_room': room not in state.room_socks,
        'user_exit': uuid not in state.uuid_sock,
        'er_Not_admin': response['sender'] not in state.roomsFile[room]['admins']
    }
    data = errors.multiple_error_handle(possible_errors, state)
    if(data): return data[0]

    #If User is already admin
    if(uuid in state.roomsFile[room]['admins']):
        payload = json.dumps({"content": f"{username} is already an admim", "type": "sys"})

    else:     
        state.roomsFile[room]['admins'].append(uuid)            
        payload = json.dumps({"content": f"{room} has made {state.uuid_user(uuid)} an ADMIN", "type":"msg"})            
        return (f'/r{room}', payload, state)
