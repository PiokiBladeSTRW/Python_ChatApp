import formatting
from session_state import state
from sql_handle import sql_db

async def dms(response: dict): 
    '''Handle Display & Storage of DMs'''
    
    # Data Arrangement
    username = state.uuid_name(response['sender_id'])
    data = (response['timestamp'], username, response['content'])

    # Writing to DB
    await sql_db.write(response['sender_id'], response['content'], int(float(response['timestamp'])))

    # DISPLAY-
    if(response['sender_id'] == state.receiver_id): 
        # Direct Message : [Time] > Message
        print(formatting.format(data, ('bt', 'a', 'c'))) 

    else:
        # Incoming Message : < sender_id : Message >
        print(formatting.format(data, ('s', 'cl', 'c', 'A')))

async def rooms(response: dict):
    '''Handle Display & Storage of Room Broadcasts'''

    # Data Arrangement
    room_uuid, user_uuid =response['sender_id'][0], response['sender_id'][1]        
    
    room_name, username = state.uuid_name(room_uuid), state.uuid_name(user_uuid)
    data = (response['timestamp'], f"[{room_name}] {username}", response['content'])

    # Writing to DB
    await sql_db.write(user_uuid, response['content'], int(float(response['timestamp'])), room_uuid)

    # DISPLAY -
    if(room_uuid == state.receiver_id):
        # Direct Room Broadcast
        print(formatting.format(data, ('bt', 's', 'cl', 'c')))

    else:
        # Incoming Room Broadcast
        print(formatting.format(data, ('s', 'cl', 'c', 'A')))