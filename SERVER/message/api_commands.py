#Solo File handling API data Request Parsing & Responding
import json

from message.utilities import utility
from server_state import state


'''# Gives user a list of online members [/online]'''
def online_list(sender_id: str) -> tuple:
    uuid_data = list(state.uuid_sock)
    uuid_data.remove(sender_id)
    
    user_data = [state.uuid_user(x) for x in uuid_data]
    data = '\n'.join(user_data)    

    return {"content": data}

'''# Gives user a list of rooms [/rooms]'''
def room_list() -> tuple:
    data = '\n'.join(state.roomName_roomUuid)
    return {"content": data}

'''# Gives user a detailed info on room [/room info]'''
def room_info(room_id: str) -> tuple:
    desc, created = state.roomsFile[room_id]['desc'], state.roomsFile[room_id]['creation']
    info_data = f"\nRoom Name: {state.roomsFile[room_id]['name']} \nDescription: {desc} \nCreated On: {created}"
    return {"content": info_data}

'''# Gives user the profile of Asked Individual [/profile get]'''
def profile_get(user_uuid: str) -> tuple:    
    if(data := utility.error_handle(user_uuid not in state.accountsFile, 'er_Invalid_user')): return json.loads(data)

    profile = state.uuidsFile[user_uuid]['profile']   
    
    data = f"{user_uuid}> {profile}"
    return {"content": data}


'''# Gives user a list of room members [/room members]'''
def room_members(room_id: str) -> tuple:    
    member_data = [x for x in state.roomsFile[room_id]['members']]
    return json.loads(utility.encode_payload(state.system_codes['room_members'], member_data, room_id))


'''# Sets Room's Description [/room desc]'''
def room_desc(response: object) -> tuple:
    room_uuid = response.receiver_id

    if(data := utility.error_handle(response.sender_id not in state.roomsFile[room_uuid]['admins'], 'er_Not_admin')): 
        return json.loads(data)

    state.roomsFile[room_uuid]['desc'] = response.content
    return {"content": 0}  

'''# Allows user to modify their profile [/profile set]'''
def profile_set(response: object) -> tuple:
    profile = response.content
    state.uuidsFile[response.sender_id]['profile'] = profile
    
    return {"content": 0}