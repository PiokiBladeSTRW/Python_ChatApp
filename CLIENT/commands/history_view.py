# HEADER
import aioconsole
import formatting
from session_state import state
from sql_handle import sql_db

'''
FIELDS: (id, sender_id, receiver_id, room_id, content, timestamp)

Primary Key: id
Optional Fields: receiver_id, room_id

Receiver_id: Signifies the Message is SENT by the user not Received
room_id: Signifies the message is a Room message. 

Receiver & Room ID, NEVER CO-EXIST. Presence of One means the other is ''
'''

async def main(uuid:str, name:str):
    '''Viewing Function'''  

    room: bool = uuid.startswith('room_')

    # Retrieve Appropriate Message History
    if(room):
        sql_query= '''SELECT * FROM msgHistory        
            WHERE room_id = ?
            ORDER BY id'''
        args = (uuid,)
    else:
        sql_query= '''SELECT * FROM msgHistory
        WHERE (sender_id = ? OR receiver_id = ?) AND room_id =''
        ORDER BY id'''
        args = (uuid, uuid)

    await sql_db.exec(sql_query, args, False)
    messages = await sql_db.cursor.fetchall()

    # Loop Through History
    for msg in messages:
        print(f"\n{msg}\n")
        
        # Format the Messages Appropriately
        if(room):
            sender = f"[{name}] {state.uuid_name(msg[1])}"
            data = (msg[5], sender, msg[4])       
            format = ('bt', 's', 'cl', 'c')     
        else:
            if(msg[1] == uuid):
                data = (msg[5], name, msg[4])
                format = ('bt', 's', 'cl', 'c')     
            else:
                data = (msg[5], state.uuidsFile[state.clientUUID], msg[4], name)
                format = ('bt', 's', 'a', 'r', 'cl', 'c')     

        # Display & Continuation Input
        print(formatting.format(data, format))

        inp = await aioconsole.ainput(">")
        if(inp == '/e'):
            return 0
        if(inp == '/o'):
            return 1  
                   
    else:
        print("\n --END OF HISTORY--")
        return 0
    
async def process_begin():
    '''Entry Function to History View'''

    print("\nIn Display: /e to Exit and /o to Change User\n")
    while True:
        name = input("ENTER USERNAME: ")

        uuid = state.name_uuid(name)
        if(uuid == 0): return

        code = await main(uuid, name)

        if(code == 0): return
        if(code == 1): continue