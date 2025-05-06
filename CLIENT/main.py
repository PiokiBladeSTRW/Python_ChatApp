import asyncio
import argparse
import requests
import websockets
import auth

from chatClient import client
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
    no_uuid = True    
    while attempt < recon_attempt:
        print("Connecting to Server... ")
        if(no_uuid):
            try:
                requests.get("http://127.0.0.1:8000/")
                user_uuid = auth.start_auth()
            except requests.exceptions.ConnectionError:
                state.log(f"API Server Failed; Reconnecting")
                attempt += 1
                await asyncio.sleep(5)
                continue
            
            no_uuid = False
            state.log(f"UUID OBTAINED: {user_uuid}")
            state.clientUUID = user_uuid

        try:
            await client.connectClient()
            exit_code = await client.start_methods()
            state.log(f"Exited Program with Exit Code {exit_code}")

            # Client Close
            if(exit_code==0): break

            # Other Issues [Add Edge cases in cases of other forms of crash instead of Server Crash]            
            attempt = 0
            continue
                    
        except ConnectionRefusedError:            
            state.log(f"Chat Server Failed; Reconnecting")
            attempt += 1
            await asyncio.sleep(5)
            continue

asyncio.run(entry())

'''Entry Point to Client; Any Time Client Closes without Exit-Code 0, it'll keep retrying connection'''