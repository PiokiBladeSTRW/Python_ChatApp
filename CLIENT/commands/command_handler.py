'''Handle Commands used by Client: Bring Changes and parse message for server if needed

Commands and Actions
    /dm <username> <msg>    : Initiates a DM with given Username as receiver_id
    /#                      : Removes receiver_id, that is closing a DM
    /exit                   : Exit                                            [Parsed as /e]
    /online                 : Online List                                     [Parsed as /o]        
    /create <room>          : Create a Room                                   [Parsed as /c+<room>]
    /join <room> <msg>      : Initiates messaging with Room as receiver_id        
    /rooms                  : List of Rooms                                   [Parsed as /r]
    /b                      : Backtracks receiver_id to Swap
'''
# Header
from session_state import state
import commands.room_cmd as room_cmd
from commands.error_display import error_display


'''========================== type: msg'''


'''Handle DMS'''
def handle_dm(args:list) -> tuple:  

    if(len(args)<2): return error_display("Invalid Arguments!")

    '''Args[0]= Username, Args[1::]= Message''' 
    uuid = state.name_uuid(args[0])
    if(uuid == 0): return (None, None)
    if(uuid.startswith('room_')): return error_display("Account of such Name doesn't Exist")


    state.receiver_id_change(uuid)
    payload = (' '.join(args[1::]), state.msgTypes['message'])
    return ('ws_send', payload)


'''========================== type : sys'''
   

'''List of every Online Client'''
def online_list(args:list) -> tuple:   
    content = [x for x in state.uuidsFile if x.startswith('user_')] 
    return ('ap_post', ("online_list", content))

'''List of every Online Room'''    
def rooms_list(args:list) -> tuple:     
    return ('ap_get', ('rooms_list', ''))

'''Profile Management'''
def profile(args:list) -> tuple:

    if(len(args)<2): return error_display("Invalid Arguments!")

    match args[0]:
        case "get": 
            uuid = state.name_uuid(args[1])
            if(uuid == 0): return (None, None)
            if(uuid.startswith('room_')): return error_display("Account of such Name doesn't Exist")
            
            return ('ap_get', ('profile_get', uuid))
        
        case "set": 
            content= ' '.join(args[1::])
            return ('ap_post', ('profile_set', content))

        case _: return error_display("Invalid Command!")


'''Exit Program'''
def close(args:list) -> tuple: 
    return ('exit', None)

'''Room Related Commands'''
def room(args:list) -> tuple: 
    
    if(len(args)<2 and args[0] not in ('members', 'info')): return error_display("Invalid Arguments!")

    if(args[0] not in ('create', 'join') and not state.receiver_id.startswith('room_')): 
        return error_display("Invalid Room")

    match args[0]:
        case "join": return room_cmd.join_room(args[1])
        case "create": return room_cmd.create_room(args[1])
        case "invite": return room_cmd.invite_user(args[1])
        case "admin": return room_cmd.admin_user(args[1])
        case "demote": return room_cmd.demote_user(args[1])
        case "kick": return room_cmd.kick_user(args[1])
        case "ban": return room_cmd.ban_user(args[1])
        case "unban": return room_cmd.unban_user(args[1])
        case "desc": return room_cmd.set_desc(args[1::])
        case "info": return room_cmd.info()
        case "members": return room_cmd.members()
        case "transfer": return room_cmd.transfer(args[1])
        case "leave": return room_cmd.leave()
        case _: return error_display("Invalid Command!")


'''========================== type : none'''


'''Reset receiver_id'''
def reset_rec(args:list) -> tuple: 
    state.receiver_id_change('')
    return (None, None)
    
'''Backtrack receiver_id'''
def back_rec(args:list) -> tuple: 
    state.receiver_id_change(state.preceiver_id)
    return (None, None)

'''Display Help'''
def chat_help(args:list) -> tuple:
    import help
    return (None, None)

'''View Message History'''
def history(args:list)->tuple:
    return ('view', None)


'''-------------------------------------'''

 
def is_command(msg:str):
    '''Check if inputted Message is a Command'''

    if(msg.startswith('/')):
        return True
    return False


def parse_command(input_cmd:str) -> tuple:       
    '''Match Command to Function''' 

    parts = input_cmd.split()    

    # Check if the command has arguments
    if(len(parts)==1):
        cmd, args = parts[0], ''
    
    else:
        cmd, args = parts[0], parts[1::]
    
    # Execute Command
    if cmd in commands: 
        state.log(f"Running Command: {cmd}")       
        return commands[cmd](args)        
    
    return error_display("Invalid Command!")
    

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

    "/profile": profile,

    "/history": history,
}


'''
Return Type: (ACTION, PAYLOAD)
ACTION : Describes action to do with the returned Payload
PAYLOAD: Returned Data

ACTION ->   'ws_send': Send Payload to chat server with pending encoding
            'ap_get': Send Payload to api server for GET
            'ap_post': Send Payload to api server for POST
            'view': Open up history_view; Not opened here to avoid async hell
            'exit': Special Handling Disconnection
            None : Client need do nothing, work is done           
'''