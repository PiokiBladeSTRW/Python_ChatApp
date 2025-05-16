import aioconsole
import requests

import interface.routing as interface
import commands.command_handler as command_handler
import commands.history_view as history
from session_state import state


async def user_input(api_address:str, chat_client:object):
    '''
    Module Responsible for User Input & Handling
    @params: 
        api_address -> Server Address of API Server
        chat_client -> Chat Client Object to directly Connect to Socket
    @returns:
        exit_code -> Determines cause of exit    
    '''

    state.log(f"Message Up & Running")

    while True:            
        msgInput = await aioconsole.ainput()            
        
        # Handle Commands
        if(command_handler.is_command(msgInput)):
            action, payload = command_handler.parse_command(msgInput)
            '''
            Possible Actions: ws_send, ap_get, ap_post, exit, None
                Websocket Payload Format: (content, type)  or ( (command, content), type='sys')
                API Payload Format: (url, content)              
            '''
            
            # Check what to do to Payload
            match action:

                case 'ws_send': 
                    # Send Data Via WebSocket
                    chat_client.exit_code = await chat_client.sendPayload(payload)

                case 'ap_get': 
                    # Get Data from API Server
                    destination = f"{api_address}/{payload[0]}/{payload[1]}"

                    response = requests.get(destination).json()
                    response['type'] = state.msgTypes['system']

                    await interface.parse_response(response)

                case 'ap_post': 
                    # Post Data to API Server
                    data = {"sender_id": state.clientUUID, "content": payload[1], "receiver_id": state.receiver_id}
                    destination = f"{api_address}/{payload[0]}"

                    response = requests.post(destination, json= data).json()

                    # If Response needs Display
                    if(response.get('content') != 0):
                        response['type'] = state.msgTypes['system']
                        await interface.parse_response(response)

                case 'exit': 
                    # Close Program [Server Down not accounted as User is Exiting Regardless]
                    await chat_client.sendPayload(
                        ((state.client_codes['user_exit'], ''), state.msgTypes['system'] ) 
                        )                 
                    chat_client.exit_code = 0                        

                case 'view':
                    # View Message History (called from here to avoid async imports)
                    await history.process_begin()

                case None: pass              
                case _: raise ValueError(f"●→ INVALID PAYLOAD ACTION RECEIVED: {action}")

        # Regular Messages
        elif(state.receiver_id):
            chat_client.exit_code = await chat_client.sendPayload( (msgInput, state.msgTypes['message']) )

        # Message with no Destination
        else:
            print("[!!ERROR: No Destination Chosen]")       
        
        # In case there is an Exit_Code; Program Shuts
        if(chat_client.exit_code): return

        print()