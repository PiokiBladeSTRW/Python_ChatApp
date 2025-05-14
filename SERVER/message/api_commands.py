#Solo File handling API data Request Parsing & Responding
from message.utilities import utility
from server_state import state

'''# Lets user close safely [/exit]'''
def user_exit() -> tuple:
    return ('*', '/exit')

'''# Gives user a list of online members [/online]'''
def online_list(response:dict) -> tuple:
    uuid_data = list(state.uuid_sock)
    uuid_data.remove(response['sender_id'])
    
    user_data = [state.uuid_user(x) for x in uuid_data]
    data = '\n'.join(user_data)    

    return ('/s', utility.encode_payload(content= data))

'''# Gives user a list of rooms [/rooms]'''
def room_list() -> tuple:
    data = '\n'.join(state.roomName_roomUuid)
    return ('/s', utility.encode_payload(content= data))

'''# Gives user a list of room members [/room members]'''
def room_members(response: dict) -> tuple:    
    member_data = [x for x in state.roomsFile[response['receiver_id']]['members']]
    return ('/s', utility.encode_payload(state.system_codes['room_members'], member_data, response['receiver_id']))

'''# Gives user a detailed info on room [/room info]'''
def room_info(response:dict) -> tuple:
    room = response['receiver_id']

    desc, created = state.roomsFile[room]['desc'], state.roomsFile[room]['creation']
    info_data = f"\nRoom Name: {room} \nDescription: {desc} \nCreated On: {created}"
    return ('/s', utility.encode_payload(content=info_data))

'''# Sets Room's Description [/room desc]'''
def room_desc(response:dict) -> tuple:
    room_uuid = response['receiver_id']

    if(data := utility.error_handle(response['sender_id'] not in state.roomsFile[room_uuid]['admins'], 'er_Not_admin')): 
        return data

    state.roomsFile[room_uuid]['desc'] = response['content']
    return ('*', None)  

'''# Gives user the profile of Asked Individual [/profile get]'''
def profile_get(response:dict) -> tuple:    
    user_uuid  = response['content']

    if(data := utility.error_handle(user_uuid not in state.accountsFile, 'er_Invalid_user')): return data

    profile = state.uuidsFile[user_uuid]['profile']   
    
    data = f"{user_uuid}> {profile}"
    return ('/s', utility.encode_payload(content= data))

'''# Allows user to modify their profile [/profile set]'''
def profile_set(response:dict) -> tuple:
    profile = response['content']
    state.uuidsFile[state.uuid_user(response['sender_id'])]['profile'] = profile

    return('*', None)   