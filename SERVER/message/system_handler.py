# Header
from server_state import state
from message.utilities import utility

'''
Commands and their Arguments:
1: Exit -> None
2: Online List -> None
3: Rooms List -> None
4: Create Room -> Room_Name
5: Room Invite -> (Room Name, Username)
6: Room Admin -> (Room Name, Username)'''


'''----------------------------------------------'''


'''# Join a Room [/room join]'''
def room_join(clientSock:object, response:dict) -> tuple:    
    room_uuid = response['receiver_id']

    #ERROR HANDLING [NOT DONE BY ERROR CLASS DUE TO SECOND CONDITION BEING MASSING AND DEPENDENT ON FIRST]
    if(data := utility.error_handle(room_uuid not in state.roomsFile, 'er_Invalid_room')): return data

    if(not(clientSock in state.room_sock[room_uuid] or state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites'])): 
        return ('/s', utility.encode_payload(state.system_codes['er_Not_room_member']))  
    
    if(state.sock_uuid[clientSock] in state.roomsFile[room_uuid]['invites']): 
        utility.modify_room(room_uuid, ('N_JOIN', 'R_INVITE'), clientSock)   
        members = [x for x in state.roomsFile[room_uuid]['members']].remove(response['sender_id'])
        return (
            (room_uuid, utility.encode_payload(state.system_codes['new_room_member'],[response['sender_id']], room_uuid)),
            ('/s', utility.encode_payload(state.system_codes['no_display'], members, room_uuid)))
    else:         
        return ('*', None)  


'''# Creates a new room [/room create]'''
def room_create(clientSock:object, response:dict) -> tuple:
    room_name = response['content'][0]

    room_uuid = utility.modify_room(None, ('CREATE',), clientSock, room_name=room_name)

    utility.modify_room(room_uuid, ('N_JOIN', 'ADMIN'), clientSock, state.sock_uuid[clientSock])    

    return ('/s', utility.encode_payload(state.system_codes['room_live'], sender_id= room_uuid))