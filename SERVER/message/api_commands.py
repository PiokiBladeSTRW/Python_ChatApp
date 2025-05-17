'''Solo File handling API data Request Parsing & Responding'''

# Header
from server_state import state

'''----------------------------------------------- API: GET'''

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
    info_data = f"Room Name: {state.roomsFile[room_id]['name']}\n Description: {state.roomsFile[room_id]['desc']}\n Current Owner: {state.roomsFile[room_id]['owner']}\n Created On: {state.roomsFile[room_id]['creation']}"
    
    return {"content": info_data}


'''# Gives user the profile of Asked Individual [/profile get]'''
def profile_get(user_uuid: str) -> tuple:    
    profile = state.uuidsFile[user_uuid]['profile']   
    
    data = f"{state.accountsFile[user_uuid]['username']}> {profile}"
    return {"content": data}

'''# Gives user a list of room members [/room members]'''
def room_members(room_id: str) -> tuple:    
    # Only API command with a System Code
    member_data = [x for x in state.roomsFile[room_id]['members']]
    
    return {"command": state.system_codes['room_members'], "content": member_data, "sender_id": room_id}


'''----------------------------------------------- API: POST'''


'''# Sets Room's Description [/room desc]'''
def room_desc(response: object) -> tuple:
    room_uuid = response.receiver_id

    if(response.sender_id not in state.roomsFile[room_uuid]['admins']):
        return {"command": state.system_codes['er_Not_admin']}

    state.roomsFile[room_uuid]['desc'] = response.content
    return {"content": 0}  


'''# Allows user to modify their profile [/profile set]'''
def profile_set(response: object) -> tuple:
    profile = response.content
    state.uuidsFile[response.sender_id]['profile'] = profile
    
    return {"content": 0}