import formatting
from session_state import state

def dms(response: dict): 
    username = state.uuid_name(response['sender_id'])
    data = (response['timestamp'], username, response['content'])

    # Direct Message : [Time] > Message
    if(response['sender_id'] == state.receiver_id): 
        print(formatting.format(data, ('bt', 'a', 'c')))  
        
    # Incoming Message : < sender_id : Message >
    else:
        print(formatting.format(data, ('s', 'cl', 'c', 'A')))

def rooms(response: dict):
    room_uuid, user_uuid =response['sender_id'][0], response['sender_id'][1]        
    
    room_name, username = state.uuid_name(room_uuid), state.uuid_name(user_uuid)
    data = (response['timestamp'], f"[{room_name}] {username}", response['content'])

    # Direct Room Broadcast
    if(room_uuid == state.receiver_id):
        print(formatting.format(data, ('bt', 's', 'cl', 'c')))

    # Incoming Room Broadcast
    else:
        print(formatting.format(data, ('s', 'cl', 'c', 'A')))