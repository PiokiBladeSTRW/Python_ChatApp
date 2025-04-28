'''Handle (bring about requried changes) and Display Incoming Data from Server'''

#Header
import formatting
import time

'''Handle Default Messages'''
def incoming_message(response:dict, state:object) -> object:
    def dms(): 
        data = (response['timestamp'], response['sender'], response['content'])

        # Direct Message : [Time] > Message
        if(data[1] == state.receiver): 
            print(formatting.format(data, ('bt', 'a', 'c')))  
            
        # Incoming Message : < Sender : Message >
        else:
            print(formatting.format(data, ('s', 'cl', 'c', 'A')))

    def rooms():
        room, username =response['sender'][0], response['sender'][1]
        if(room not in state.clientRoomsFile): state.clientRoomsFile.append(room)

        data = (response['timestamp'], f"[{room}] {username}", response['content'])

        # Direct Room Broadcast
        if(room == state.receiver[2::]):
            print(formatting.format(data, ('bt', 's', 'cl', 'c')))

        # Incoming Room Broadcast
        else:
            print(formatting.format(data, ('s', 'cl', 'c', 'A')))

    # Check whether the message is a DM or Room Message
    if( type(response['sender']) == list):        
        rooms()        
    else:
        dms()

    return state

'''Handle User Loggings'''
def online_user(response:dict, state:object) -> object:
    data = ('', response['sender'], "is ONLINE")

    # OUTPUT : [Sender 'is Online'
    print(formatting.format(data, ('s', 'c', 'S')))

    return state

'''Handle System Messages'''
def system(response:dict, state:object) -> object:  
    
    # Guard Clause  (if not a command)
    if(not response['command']):
        data = ('', '{System}', response['content']) 

        print(formatting.format(data, ('s', 'cl', 'c')))    
        return state
    

    ''' Handle Different Types of Sys Commands. More Dynamic (& confusing) than other modules'''

    # Room Based System Message
    if(response.get('sender').startswith('/r')):
        args = [response['sender'][2::]] + list(response['content'])
        disp_msg = state.sys_code_msg[response['command']]

        if(response['command'] in state.sys_format): disp_msg = disp_msg.format(*args)

        data = ('', f"[{args[0]}] {{System}}", disp_msg)
    
    else:
        args = list(response.get('content'))
        disp_msg = state.sys_code_msg[response['command']]

        # Excuse these magic values
        receiver_change= (101,)
        receiver_change_force = (204, 205)
        
        # If Needs Formatting
        if(response['command'] in state.sys_format): disp_msg = disp_msg.format(*args)

        # Change Receiver if currently in contact or by force
        if(response['command'] in receiver_change and state.receiver== args[0]):
            state.receiver_change('')
        
        elif(response['command'] in receiver_change_force):
            state.receiver_change('')

        data = ('', "{System}", disp_msg)

    print(formatting.format(data, ('s', 'cl', 'c')))
    return state
    

'''-------------------------------------'''


'''Handle Responses'''
def parse_response(response:dict, state:object) -> object: 

    # For future purpose of Storing in DB
    if(not response.get('timestamp')): response['timestamp'] = time.time()

    if(response['type'] in types): 
        state = types[response['type']](response, state)
        return state
    else:
        raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")
    

'''Response Types'''
types ={
    "msg": incoming_message,
    "auth": online_user,
    "sys": system
}