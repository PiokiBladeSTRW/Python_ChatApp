import formatting
from session_state import state

def args_conversion(content:list, args:list =[]): 
    data= []
    for argument in content:
        if(argument.startswith('user_') or argument.startswith('room_')):
            data.append(state.uuid_name(argument))

        else:
            data.append(argument)
    
    return args + data

def disp_formatting(command: int, args:list): 
    disp_msg = state.sys_code_msg[command]

    if(command in state.sys_format): 
        
        if(disp_msg == '0'):                
            return '\n'.join(args[1::])  

        else:
            return disp_msg.format(*args)
        
def special_commands(response:dict, args:list): 
    command = response['command']

    # No Display
    if(command == state.system_codes['no_display']):
        return 0
    
    # Room Data
    if(command == state.system_codes['room_data']):
        state.roomsFile[response['sender_id']] = args[1::]
        return 0
    
    # Room Member
    if(command == state.system_codes['new_room_member']):
        state.roomsFile[response['sender_id']].append(args[1])
        return
    
    # If Just Created Room, update Receiver
    if(command == state.system_codes['room_live']):
        state.roomsFile[response['sender_id']] = []
        state.receiver_id_change(response['sender_id'])
        return
    
    # If Current Receiver is no longer Contactable, reset Receiver
    rec_change =(
        state.system_codes['user_exit'], state.system_codes['got_kicked'], state.system_codes['got_banned'], state.system_codes['er_Invalid_user'], state.system_codes['er_Invalid_room'], state.system_codes['er_Not_room_member'])
    if(command in rec_change and state.receiver_id == args[0]):
        state.receiver_id_change('', False)
        return

    # If Tried to join a non-existent room, reset Receiver
    if(command == state.system_codes['er_Room_exists']):
        state.receiver_id_change('', False)
        return


'''---------------------------------------------------'''


def rooms(response:dict):
    # Format: [0] = Room ; [1] usually Username
    args = []
    args.append(state.uuid_name(response['sender_id']))

    # If there are arguments
    if(response.get('content')):
        args = args_conversion(response['content'], args)

    if(response['command'] in state.modify_codes):
        code = special_commands(response, args)
        if(code==0): return

    disp_msg = disp_formatting(response['command'], args)

    data = ('', f"[{args[0]}] {{System}}", disp_msg)
    print(formatting.format(data, ('s', 'cl', 'c')))
    return


def std(response:dict):
    # If Arguments
    if(response.get('content')): 
        args = args_conversion(response['content'])

    if(response['command'] in state.modify_codes):
        code = special_commands(response, args)
        if(code==0): return

    disp_msg = disp_formatting(response['command'], args)

    data = ('', "{System}", disp_msg)
    print(formatting.format(data, ('s', 'cl', 'c')))