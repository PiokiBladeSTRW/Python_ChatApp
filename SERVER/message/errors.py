import json

error_list = []

'''Error Handling'''
def error_handle(condition:bool, error:str,  state: object) -> tuple:
    '''Key States whether or not the 'Error' is a Code or Not'''
    if(condition):
        payload = json.dumps({'content': state.codes[error], 'type': "sys"})
        return('/s', payload, state)
    
    return None

def parse_error() -> list:
    data = [x for x in error_list if x != None]
    error_list = []
    return data

# Used by room related commands especially Invite and Admin
def common_room_errors(room:str, uuid:str, state:object) -> list:
    error_list.append( error_handle(room not in state.room_socks, 'er_Invalid_room', state) )

    error_list.append( error_handle(uuid not in state.uuid_sock, 'user_exit', state) )

    error_list.append( error_handle(uuid not in state.roomsFile[room]['admins'], 'er_Not_admin' , state))

    #Errors Caught:
    return parse_error()