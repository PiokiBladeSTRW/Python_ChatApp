'''
Functions to be Utilized for Room Subcommands. 
<> Wraps indicate the Function is used only within this very Module
'''


'''<Obtaining Room Name>'''
def obtain_room(receiver) -> str:
    if(receiver.startswith('/r')):
        return receiver[2::]
    
    print("Invalid Room")
    return None

'''----------------------------------------------'''

'''Join a Room'''
def join_room(args:list, state:object) -> tuple: 
    '''Args[0] = Room, Args[1::] = Message'''

    state.receiver_change('/r'+args[0])
    payload = (' '.join(args[1::]), state.msgTypes['message'])
    return ('send', payload, state)    
    
'''Create a Room'''
def create_room(room_name:str, state:object) -> tuple: 
    state.receiver_change('/r'+room_name)
                
    payload = ('/c'+room_name, state.msgTypes['system'])
    return ('send', payload, state)

'''Invite user to Room'''
def invite_user(username:str, state:object) -> tuple:
    room = obtain_room(state.receiver)
    if(room == None): return None

    payload = ('/i'+room+';'+username, state.msgTypes['system'])
    return ('send', payload, state)

'''Make user an Admin'''
def admin_user(username:str, state:object) -> tuple:
    room = obtain_room(state.receiver)
    if(room == None): return None

    payload = ('/a'+room+';'+username, state.msgTypes['system'])
    return ('send', payload, state)