# HEADER (chonky one)
import asyncio
import argparse
import requests
import websockets

import auth
import commands.user_input as input_module
from chatClient import chat_client
from session_state import state
from sql_handle import sql_db

async def entry():
    '''
    Sets Up USER and Attempts Connection to Server;
    In case Server is or goes down, attempts Reconnection;
    Performs Authentication, Socket Booting, Message Input and Handling.
    '''

    # Connect to Proper Files based on User Profile
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

        # Handle User Authentication ; username = False, unless user just Registered
        if(not user_uuid):
            try:                
                requests.get(api_address)               
                user_uuid, username = auth.start_auth()   

            except requests.exceptions.ConnectionError:
                state.log(f"API Server Failed; Reconnecting")
                attempt += 1
                await asyncio.sleep(5)
                continue            
            
            state.log(f"UUID OBTAINED: {user_uuid}")
            state.clientUUID = user_uuid

            # REGISTRATION. Set Files Up with Data
            if(username):

                # UUID-Mappin
                state.uuidsFile[user_uuid] = username
                state.name_uuid_dict[username] = user_uuid

                # SQL Table Creation
                sql_query = '''CREATE TABLE IF NOT EXISTS msgHistory(
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'sender_id' TEXT,
                'receiver_id' TEXT DEFAULT '',
                'room_id' TEXT DEFAULT '',
                'content' TEXT,
                'timestamp' INTEGER)'''     
                await sql_db.write(sql_query)


        # Socket Connection Establishment
        try:            
            await chat_client.connectClient()
            exit_code = await start_methods()
            state.log(f"Exited Program with Exit Code {exit_code}")

            # Client Closed Properly
            if(exit_code==0): break

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

    # If We Run out of Attempts of Reconnection
    else:
        print("\nServer taking too long, Try Later")        


async def start_methods():
    '''
    Start all the Tasks Required Here for Centralized Control
    Tasks: 
        (Input) Message_Input & Handling
        (Socket) Receiving Message, Updating Files, Sending HeartBeats
    '''

    tasks = [
        asyncio.create_task(input_module.user_input(api_address, chat_client)),
        asyncio.create_task(chat_client.receive()),
        asyncio.create_task(chat_client.heartbeat()),
        asyncio.create_task(chat_client.fileHandle())
    ]
    state.log(f"Starting Co-routines")

    # Start Tasks until anyone has a `return`
    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    state.log("Program Exited")     
    await chat_client.clientSock.close()

    # Cancel The Processes if Reconnection will be Attempted [As cleanup() will clean otherwise]
    if(chat_client.exit_code != 0):
        for task in asyncio.all_tasks():            
            if(task != asyncio.current_task()):
                task.cancel()
                try: await task
                except asyncio.CancelledError: pass
    
    return chat_client.exit_code


async def cleanup():
    # Close All tasks + Close SQL connector
    for task in asyncio.all_tasks():            
        if(task != asyncio.current_task()):
            task.cancel()
            try: await task
            except asyncio.CancelledError: pass

    await sql_db.conn.close()


# __MAIN__
api_address = "http://127.0.0.1:8000/"

'''Connect and Reconnect to Server UNTIL Error or User Exits. Then Cleanup'''
try:
    asyncio.run(entry())

except Exception as e:
    print(f"ERROR OCCURED: {e}")
    
finally:   
    asyncio.run(cleanup())