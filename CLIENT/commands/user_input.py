import aioconsole
import requests

import interface.routing as interface
import commands.command_handler as command_handler
import commands.history_view as history
from session_state import state


async def user_input(api_address:str, chat_client:object):
    '''
    Module Responsible for User Input
    '''

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