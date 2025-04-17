'''Handle Commands used by Client: Bring Changes and parse message for server if needed'''

'''
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

'''Handle DMS'''
def handle_dm(args:list, state:object):      
    receiver_change(state, args[0])
    payload = (' '.join(args[1::]), state.msgTypes['message'])
    return ('send', payload, state)

'''Room Related Commands'''
def room(args:list, state:object): 
    '''Join a Room'''
    def join_room(args:list, state:object): 
        receiver_change(state, '/r'+args[0])
        payload = (' '.join(args[1::]), state.msgTypes['message'])
        return ('send', payload, state)    
        
    '''Create a Room'''
    def create_room(args:list, state:object): 
        receiver_change(state, '/r'+args[0])
                    
        payload = ('/c'+args[0], state.msgTypes['system'])
        return ('send', payload, state)
    
    match args[0]:
        case "join": return join_room(args[1::], state)
        case "create": return create_room(args[1::], state)
        case _: print("INVALID COMMAND")
        
    return (None, None, state)

'''Reset Receiver'''
def reset_rec(args:list, state:object): 
    receiver_change(state, '')
    return (None, None, state)
    
'''Backtrack Receiver'''
def back_rec(args:list, state:object): 
    receiver_change(state, state.pReceiver)
    return (None, None, state)

'''Exit Program'''
def close(args:list, state:object): 
    return ('exit', None, state)
    
'''List of every Online Client'''
def online_list(args:list, state:object): 
    payload = ('/o', state.msgTypes['system'])    
    return ('send', payload, state)

'''List of every Online Room'''    
def rooms_list(args:list, state:object): 
    payload = ('/r', state.msgTypes['system'])
    return ('send', payload, state)

'''Display Help'''
def chat_help(args:list, state:object):
    import help
    return (None, None, state)


'''-------------------------------------'''


'''Change Receivers'''
def receiver_change(state, receiver):
    state.pReceiver = state.receiver
    state.receiver = receiver
    
    if(receiver==''): receiver = 'No One'
    
    if(receiver.startswith('/r')):
        print('', "="*25, f"Now Chatting in {receiver[2::]}", "="*25, sep='\n')
        return

    print('', "="*25, f"Now Chatting with {receiver}", "="*25, sep='\n')
    
'''Check if inputted Message is a Command'''
def is_command(msg:str):
    if(msg.startswith('/')):
        return True
    return False

'''Match Command to Function'''
def parse_command(input_cmd:str, state:object):    
    parts = input_cmd.split()    

    #check if the command has arguments
    if(len(parts)==1):
        cmd, args = parts[0], ''
    else:
        cmd, args = parts[0], parts[1::]        
    
    if cmd in commands:        
        data = commands[cmd](args, state)
        return data
    
    print("INVALID COMMAND")
    return (None, None, state)
    

'''Convert Command to Function call in One Step'''
commands = {
    "/dm": handle_dm, 
    "/room": room,
    "/#": reset_rec,
    "/b": back_rec,
    "/exit": close,    
    "/online": online_list,
    "/rooms": rooms_list,
    "/help": chat_help,    
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