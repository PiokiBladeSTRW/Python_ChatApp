
'''Handle DMS'''
def handle_dm(args:str, state:dict):      
    receiver_change(state, args[0])
    payload = (' '.join(args[1::]), 'msg')
    return ('send', payload, state)

'''Join a Room'''
def join_room(args:str, state:dict): 
    receiver_change(state, '/r'+args[0])
    payload = (' '.join(args[1::]), 'msg')
    return ('send', payload, state)

'''Reset Receiver'''
def reset_rec(args:str, state:dict): 
    receiver_change(state, '')
    return (None, None, state)
    
'''Backtrack Receiver'''
def back_rec(args:str, state:dict): 
    receiver_change(state, state['pReceiver'])
    return (None, None, state)
    
'''Create a Room'''
def create_room(args:str, state:dict): 
    receiver_change(state, '/r'+args[0])
                
    payload = ('/c'+args[0], 'sys')
    return ('send', payload, state)

'''Exit Program'''
def close(args:str, state:dict): 
    return ('exit', None, state)
    
'''List of every Online Client'''
def online_list(args:str, state:dict): 
    payload = ('/o', 'sys')    
    return ('send', payload, state)

'''List of every Online Room'''    
def rooms_list(args:str, state:dict): 
    payload = ('/r', 'sys')
    return ('send', payload, state)


'''-------------------------------------'''


'''Change Receivers'''
def receiver_change(state, receiver):
    state['pReceiver'] = state['receiver']
    state['receiver'] = receiver
    
    if(receiver==''): receiver = 'No One'
    
    if(receiver.startswith('/r')):
        print('', "="*25, f"Now Chatting in {receiver[2::]}", "="*25, sep='\n')
        return

    print('', "="*25, f"Now Chatting with {receiver}", "="*25, sep='\n')


'''-------------------------------------'''


'''Check if inputted Message is a Command'''
def is_command(msg:str):
    if(msg.startswith('/')):
        return True
    return False

'''Match Command to Function'''
def parse_command(input_cmd:str, state:dict):    
    parts = input_cmd.split()    

    if(len(parts)==1):
        cmd, args = parts[0], ''
    else:
        cmd, args = parts[0], parts[1::]        

    if cmd in commands:        
        data = commands[cmd](args, state)            
        return data
    else:
        print("INVALID COMMAND")
        return (None, None, state)

'''COMMANDS'''
commands = {
    "/dm": handle_dm,
    "/join": join_room,
    "/#": reset_rec,
    "/b": back_rec,
    "/create": create_room,
    "/exit": close,
    "/online": online_list,
    "/rooms": rooms_list
}


'''-------------------------------------'''


'''
Return Type: (ACTION, PAYLOAD, STATE)
ACTION : Describes action to do with the returned Payload
PAYLOAD: Returned Data
STATE  : Updates Class Variables of Clients.

ACTION ->   'send': Send Payload to server with pending encoding
            'exit': Special Handling Disconnection
            None : Client need do nothing, work is done           
'''

'''
Check for Command
    [If parsed, that implies the command is receied by Server (type:sys)]

    /dm <username> <msg>    : Initiates a DM with given Username as Receiver
    /#                      : Removes Receiver, that is closing a DM
    /exit                   : Exit                                            [Parsed as /e]
    /online                 : Online List                                     [Parsed as /o]        
    /create <room>          : Create a Room                                   [Parsed as /c+<room>]
    /join <room> <msg>      : Initiates messaging with Room as Receiver        
    /rooms                  : List of Rooms                                   [Parsed as /r]
    /b                      : Backtracks Receiver to Swap
'''