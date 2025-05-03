'''Handle Commands used by Client: Bring Changes and parse message for server if needed

Commands and Actions
    /dm <username> <msg>    : Initiates a DM with given Username as Receiver
    /#                      : Removes Receiver, that is closing a DM
    /exit                   : Exit                                            [Parsed as /e]
    /online                 : Online List                                     [Parsed as /o]        
    /create <room>          : Create a Room                                   [Parsed as /c+<room>]
    /join <room> <msg>      : Initiates messaging with Room as Receiver        
    /rooms                  : List of Rooms                                   [Parsed as /r]
    /b                      : Backtracks Receiver to Swap
'''
# Header
import commands.room_cmd as room_cmd
import commands.error_handle as errors


'''========================== type: msg'''


'''Handle DMS'''
def handle_dm(args:list, state:object) -> tuple:  

    if(len(args)<2): return errors.error_handle("Invalid Arguments!", state)

    '''Args[0]= Username, Args[1::]= Message''' 
    state.receiver_change(args[0])
    payload = (' '.join(args[1::]), state.msgTypes['message'])
    return ('send', payload, state)

'''========================== type : sys'''
   

'''List of every Online Client'''
def online_list(args:list, state:object) -> tuple: 
    payload = ((state.client_codes['online_list'], ''), state.msgTypes['system'])    
    return ('send', payload, state)

'''List of every Online Room'''    
def rooms_list(args:list, state:object) -> tuple: 
    payload = ((state.client_codes['rooms_list'], ''), state.msgTypes['system'])
    return ('send', payload, state)

'''Exit Program'''
def close(args:list, state:object) -> tuple: 
    return ('exit', None, state)


'''========================== type : none'''


'''Reset Receiver'''
def reset_rec(args:list, state:object) -> tuple: 
    state.receiver_change('')
    return (None, None, state)
    
'''Backtrack Receiver'''
def back_rec(args:list, state:object) -> tuple: 
    state.receiver_change(state.pReceiver)
    return (None, None, state)

'''Display Help'''
def chat_help(args:list, state:object) -> tuple:
    import help
    return (None, None, state)


'''========================== type : depends'''


'''Room Related Commands'''
def room(args:list, state:object) -> tuple: 

    if(len(args)<2): return errors.error_handle("Invalid Arguments!", state)

    match args[0]:
        case "join": data = room_cmd.join_room(args[1], state)
        case "create": data = room_cmd.create_room(args[1], state)
        case "invite": data = room_cmd.invite_user(args[1], state)
        case "admin": data = room_cmd.admin_user(args[1], state)
        case _: return errors.error_handle("Invalid Command!", state)

    return data


'''-------------------------------------'''

 
'''Check if inputted Message is a Command'''
def is_command(msg:str):
    if(msg.startswith('/')):
        return True
    return False

'''Match Command to Function'''
def parse_command(input_cmd:str, state:object) -> tuple:    
    parts = input_cmd.split()    

    # Check if the command has arguments
    if(len(parts)==1):
        cmd, args = parts[0], ''
    
    else:
        cmd, args = parts[0], parts[1::]
    
    # Execute Command
    if cmd in commands: 
        state.log(f"Running Command: {cmd}")       
        data = commands[cmd](args, state)
        return data
    
    return errors.error_handle("Invalid Command!", state)
    

'''Convert Command to Function call in One Step'''
commands = {
    "/dm": handle_dm,

    "/online": online_list,
    "/rooms": rooms_list,  
    "/exit": close,  

    "/#": reset_rec,
    "/b": back_rec,      
    "/help": chat_help, 

    "/room": room,
}


'''
Return Type: (ACTION, PAYLOAD, STATE)
ACTION : Describes action to do with the returned Payload
PAYLOAD: Returned Data
STATE  : Updates Class Variables of Clients.

ACTION ->   'send': Send Payload to server with pending encoding
            'exit': Special Handling Disconnection
            None : Client need do nothing, work is done           
'''