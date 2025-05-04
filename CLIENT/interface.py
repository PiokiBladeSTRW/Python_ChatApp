'''Handle (bring about requried changes) and Display Incoming Data from Server'''

#Header
import formatting
import time

from session_state import state

'''Handle Default Messages'''
def incoming_message(response:dict):
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

'''Handle User Loggings'''
def online_user(response:dict):
    data = ('', response['sender'], "is ONLINE")

    # OUTPUT : [Sender 'is Online'
    print(formatting.format(data, ('s', 'c', 'S')))

'''Handle System Messages'''
def system(response:dict):  
    '''Only Module where response['content'] is not guranteed'''
    
    # Guard Clause  (if not a command)
    if(not response['command']):
        data = ('', '{System}', response['content']) 

        print(formatting.format(data, ('s', 'cl', 'c')))           
        return 
    

    ''' Handle Different Types of Sys Commands. More Dynamic (& confusing) than other modules'''

    # Room Based System Message
    if(response.get('sender')):
        '''
        As of now, only room has sender tag, in case of future aversion, add within if-else
        '''

        args = [response['sender'][2::]]
        if(response.get('content')): args += response['content']
        
        disp_msg = state.sys_code_msg[response['command']]        

        if(response['command'] in state.sys_format): disp_msg = disp_msg.format(*args)

        data = ('', f"[{args[0]}] {{System}}", disp_msg)
        print(formatting.format(data, ('s', 'cl', 'c')))
        return
    

    '''Normal System Prompts'''
    
    if(response.get('content')): args = list(response.get('content'))        
    disp_msg = state.sys_code_msg[response['command']]

    if(response['command'] in state.sys_format): disp_msg = disp_msg.format(*args)

    # Change Receiver if currently in contact or by force 
    if(response['command'] in state.receiver_change_codes and state.receiver == args[0]):
        state.receiver_change('')
    
    elif(response['command'] in state.receiver_change_codes):
        state.receiver_change('')

    data = ('', "{System}", disp_msg)
    print(formatting.format(data, ('s', 'cl', 'c')))
    

'''-------------------------------------'''


'''Handle Responses'''
def parse_response(response:dict): 
    # For future purpose of Storing in DB
    if(not response.get('timestamp')): response['timestamp'] = time.time()

    if(response['type'] in types):          
        types[response['type']](response)        
    else:                
        raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")
    

'''Response Types'''
types ={
    "msg": incoming_message,
    "con": online_user,
    "sys": system
}