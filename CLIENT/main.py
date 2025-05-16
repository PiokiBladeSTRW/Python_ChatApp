import asyncio
import aioconsole
import argparse
import requests
import websockets

import interface.routing as interface
import auth
import commands.history_view as history
import commands.command_handler as command_handler
from chatClient import chat_client
from session_state import state
from sql_handle import sql_db

async def entry():
    # Basic Setup
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=str, required=True)
    args = parser.parse_args()

    state.profileBased(args.profile)   
    state.log(f"Event Loop started w/ Profile {args.profile}")

    await sql_db.setup(args.profile)

    # Connect & Reconnect Mechanism
    recon_attempt = 20
    attempt = 0      
    user_uuid = ''
    while attempt < recon_attempt:
        print("Connecting to Server... ")

        # Handle User Authentication
        if(not user_uuid):
            try:
                requests.get(api_address)
                user_uuid, username = auth.start_auth()

                # Create a History.db if not existing already
                sql_query = '''CREATE TABLE IF NOT EXISTS msgHistory(
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'sender_id' TEXT,
                'room_id' TEXT,
                'content' TEXT,
                'timestamp' INTEGER)'''     
                await sql_db.write(sql_query)             

            except requests.exceptions.ConnectionError:
                state.log(f"API Server Failed; Reconnecting")
                attempt += 1
                await asyncio.sleep(5)
                continue            
            
            state.log(f"UUID OBTAINED: {user_uuid}")
            state.clientUUID = user_uuid
            # If Username is returned, i.e, Registration
            if(username):
                state.uuidsFile[user_uuid] = username
                state.name_uuid_dict[username] = user_uuid

        try:
            await chat_client.connectClient()
            exit_code = await start_methods()
            state.log(f"Exited Program with Exit Code {exit_code}")

            # Client Close
            if(exit_code==0): 
                await sql_db.conn.close()
                break

            # Other Issues [Add Edge cases in cases of other forms of crash instead of Server Crash]
            chat_client.exit_code=None                   
            attempt = 0
            print("Server Down. Attempting Retry [NOTE: Next message typed isn't responsive]")
            await asyncio.sleep(3)
            continue
                    
        except (ConnectionRefusedError, websockets.exceptions.ConnectionClosedError):            
            state.log(f"Chat Server Failed; Reconnecting")
            attempt += 1
            await asyncio.sleep(5)
            continue

    else:
        print("\nServer taking too long, Try Later")
        await sql_db.conn.close()

async def start_methods():
    tasks = [
        asyncio.create_task(user_input()),
        asyncio.create_task(chat_client.receive()),
        asyncio.create_task(chat_client.heartbeat()),
        asyncio.create_task(chat_client.fileHandle())
    ]
    state.log(f"Starting Co-routines")
    #Remove var later
    completed_task = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    state.log("Program Exited")     
    await chat_client.clientSock.close()

    # Cancel The
    for task in asyncio.all_tasks():            
        if(task != asyncio.current_task()):
            task.cancel()
            try: await task
            except asyncio.CancelledError: pass
    
    return chat_client.exit_code


async def user_input():
    state.log(f"Message Up & Running")
    while True:            
        msgInput = await aioconsole.ainput()            
        
        if(command_handler.is_command(msgInput)):
            action, payload = command_handler.parse_command(msgInput)
            '''Action: ws_send, ap_get, ap_post, exit, None
                Websocket Payload Format: (content, type)  
                API Format: (url, content)              
                '''
            
            # Check what to do to Payload
            match action:
                case 'ws_send': chat_client.exit_code = await chat_client.sendPayload(payload)

                case 'ap_get': 
                    response = requests.get(f"{api_address}/{payload[0]}/{payload[1]}").json()
                    response['type'] = state.msgTypes['system']
                    await interface.parse_response(response)

                case 'ap_post':                     
                    data = {"sender_id": state.clientUUID, "content": payload[1], "receiver_id": state.receiver_id}
                    response = requests.post(f"{api_address}/{payload[0]}", json= data).json()
                    if(response.get('content') != 0):
                        response['type'] = state.msgTypes['system']
                        await interface.parse_response(response)

                case 'exit': 
                    chat_client.exit_code = await chat_client.sendPayload(
                        ((state.client_codes['user_exit'], ''), state.msgTypes['system']) )                        
                    chat_client.exit_code = 0                        

                case 'view':
                    await history.process_begin()

                case None: pass              
                case _: raise ValueError(f"●→ INVALID PAYLOAD ACTION RECEIVED: {action}")

        elif(state.receiver_id):
            chat_client.exit_code = await chat_client.sendPayload( (msgInput, state.msgTypes['message']) )

        else:
            print("[!!ERROR: No Destination Chosen]")       
        
        if(chat_client.exit_code): return

        print()

async def cleanup():
    for task in asyncio.all_tasks():            
        if(task != asyncio.current_task()):
            task.cancel()
            try: await task
            except asyncio.CancelledError: pass

    await sql_db.conn.close()


api_address = "http://127.0.0.1:8000/"
try:
    asyncio.run(entry())
except KeyboardInterrupt:
    asyncio.run(cleanup())

'''Entry Point to Client; Any Time Client Closes without Exit-Code 0, it'll keep retrying connection'''