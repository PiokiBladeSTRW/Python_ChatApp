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

    print(await sql_db.cursor.fetchall())
    for msg in messages:

        if(room):
            sender = f"[{name}] {state.uuid_name(msg['sender_id'])}"
            data = (msg['timestamp'], sender, msg['content'])
        else:
            data = (msg['timestamp'], name, msg['content'])

        print(formatting.format(data, ('bt', 's', 'cl', 'c')))

        inp = await aioconsole.ainput(">")
        if(inp == '/e'):
            return 0
        if(inp == '/o'):
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