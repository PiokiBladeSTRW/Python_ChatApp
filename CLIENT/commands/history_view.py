import aioconsole
import formatting
from session_state import state
from sql_handle import sql_db


async def main(uuid:str, name:str):     
    sql_query= '''SELECT * FROM msgHistory
    WHERE sender_id = ?
    ORDER BY id'''

    messages = await sql_db.read(sql_query, (uuid,))
    
    room = uuid.startswith('room_')

    for msg in messages:
        # msg : (id, sender_id, room_id, content, timestamp)
        if(room):
            sender = f"[{name}] {state.uuid_name(msg[1])}"
            data = (msg[4], sender, msg[3])
        else:
            data = (msg[4], name, msg[3])

        print(formatting.format(data, ('bt', 's', 'cl', 'c')))

        inp = await aioconsole.ainput(">")
        if(inp == '/e'):
            return 0
        if(inp == '/o'):
            return 1             
    else:
        print("\n --END OF HISTORY--")
        return 1
    
async def process_begin():
    print("\nIn Display: /e to Exit and /o to Change User\n")
    while True:
        name = input("ENTER USERNAME: ")

        uuid = state.name_uuid(name)
        if(uuid == 0): return

        code = await main(uuid, name)

        if(code == 0): return
        if(code == 1): continue