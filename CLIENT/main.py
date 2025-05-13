import asyncio
import argparse
import requests
import websockets

from apiClient import apiClient
from chatClient import chatClient
from session_state import state

async def entry():

    # Basic Setup
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=str, required=True)
    args = parser.parse_args()

    state.profileBased(args.profile)   
    state.log(f"Event Loop started w/ Profile {args.profile}")

    # Connect & Reconnect Mechanism
    recon_attempt = 20
    attempt = 0      
    while attempt < recon_attempt:
        print("Connecting to Server... ")

        # Handle User Authentication
        if(not user_uuid):
            try:
                requests.get("http://127.0.0.1:8000/")
                user_uuid, username = auth.start_auth()                
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


            # await client.connectClient()
            # exit_code = await client.start_methods()
            # state.log(f"Exited Program with Exit Code {exit_code}")

            # # Client Close
            # if(exit_code==0): break

            # # Other Issues [Add Edge cases in cases of other forms of crash instead of Server Crash]       
            # client.exit_code =None     
            # attempt = 0
            # print("Server Down. Attempting Retry [NOTE: Next message typed isn't responsive]")
            # await asyncio.sleep(3)
            # continue
                    
        except (ConnectionRefusedError, websockets.exceptions.ConnectionClosedError):            
            state.log(f"Chat Server Failed; Reconnecting")
            attempt += 1
            await asyncio.sleep(5)
            continue

asyncio.run(entry())

'''Entry Point to Client; Any Time Client Closes without Exit-Code 0, it'll keep retrying connection'''