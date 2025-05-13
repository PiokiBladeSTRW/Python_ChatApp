'''Handle (bring about requried changes) and Display Incoming Data from Server'''

#Header
import formatting
import time

from session_state import state

'''Handle Default Messages'''
def incoming_message(response:dict):
    def dms(): 
        username = state.uuid_name(response['sender_id'])
        data = (response['timestamp'], username, response['content'])

        # Direct Message : [Time] > Message
        if(response['sender_id'] == state.receiver_id): 
            print(formatting.format(data, ('bt', 'a', 'c')))  
            
        # Incoming Message : < sender_id : Message >
        else:
            print(formatting.format(data, ('s', 'cl', 'c', 'A')))

    def rooms():
        room_uuid, user_uuid =response['sender_id'][0], response['sender_id'][1]        
        
        room_name, username = state.uuid_name(room_uuid), state.uuid_name(user_uuid)
        data = (response['timestamp'], f"[{room_name}] {username}", response['content'])

        # Direct Room Broadcast
        if(room_uuid == state.receiver_id):
            print(formatting.format(data, ('bt', 's', 'cl', 'c')))

        # Incoming Room Broadcast
        else:
            print(formatting.format(data, ('s', 'cl', 'c', 'A')))

    # Check whether the message is a DM or Room Message
    if( type(response['sender_id']) == list):         
        rooms()        
    else:
        dms()

'''Handle User Loggings'''
def online_user(response:dict):
    username = state.uuid_name(response['sender_id'])
    data = ('', username, "is ONLINE")

    # OUTPUT : [sender_id 'is Online'
    print(formatting.format(data, ('s', 'c', 'S')))

'''Handle System Messages'''
def system(response:dict):  
    '''Only Module where response['content'] is not guranteed'''
    
    # Guard Clause  (if not a command)
    if(not response.get('command')):
        data = ('', '{System}', response['content']) 

        print(formatting.format(data, ('s', 'cl', 'c')))           
        return 
    

    ''' Handle Different Types of Sys Commands. More Dynamic (& confusing) than other modules'''

    #Special Commands [aka Return]
    if(response['command'] in state.special_commands):
        
        # Force Kick
        if(response['command'] == state.system_codes['session_active']): 
            state.log(f"Tried Logging with an Active Session; Disconnecting")
            print(formatting.format(('', '{System}', state.sys_code_msg[response['command']]), ('s', 'cl', 'c')))
            return 'kick'

    # Room Based System Message
    if(response.get('sender_id')):
        '''
        As of now, only room has sender_id tag, in case of future aversion, add within if-else
        '''
        # Format: [0] = Room ; [1] usually Username
        args = []
        args.append(state.uuid_name(response['sender_id']))
        if(response.get('content')):
            data= []
            for argument in response['content']:
                if(argument.startswith('user_') or argument.startswith('room_')):
                    data.append(state.uuid_name(argument))
                else:
                    data.append(argument)
            args += data    

        if(response['command'] == state.system_codes['no_display']):            
            return

        # If Room was created and UUID is available, Join
        if(response['command'] == state.system_codes['room_live']):
            state.receiver_id_change(response['sender_id'])

        # If Have to Change
        if(response['command'] in state.change_codes and state.receiver_id == args[0]):
            state.receiver_id_change('', False)

        disp_msg = state.sys_code_msg[response['command']]   

        if(response['command'] in state.sys_format): 
            #LINEAR-DISPLAY
            if(disp_msg == '0'):                
                disp_msg = '\n'.join(args[1::])               
            else:
                disp_msg = disp_msg.format(*args)

        data = ('', f"[{args[0]}] {{System}}", disp_msg)
        print(formatting.format(data, ('s', 'cl', 'c')))
        return
    

    '''Normal System Prompts'''   
    if(response.get('content')): args = list(response.get('content'))

    if(response['command'] in state.sys_uuid_format):
        data= []
        for arg in args:
            if(arg.startswith('user_') or arg.startswith('room_')):
                data.append(state.uuid_name(arg))
            else:
                data.append(arg)
        args = data

    if(response['command'] == state.system_codes['no_display']): return

    # Change receiver_id if currently in contact or by force 
    if(response['command'] in state.change_codes and state.receiver_id == response['sender_id']):
        state.receiver_id_change('', False)
    
    elif(response['command'] in state.force_change_codes):
        state.receiver_id_change('', False)

    disp_msg = state.sys_code_msg[response['command']]


    if(response['command'] in state.sys_format): 
        #LINEAR-DISPLAY
        if(disp_msg == '0'):                
            disp_msg = '\n'.join(args[1::])               
        else:
            disp_msg = disp_msg.format(*args)

    data = ('', "{System}", disp_msg)
    print(formatting.format(data, ('s', 'cl', 'c')))
    

'''-------------------------------------'''


'''Handle Responses'''
def parse_response(response:dict): 
    # For future purpose of Storing in DB
    if(not response.get('timestamp')): response['timestamp'] = time.time()

    if(response['type'] in types):          
        return types[response['type']](response)        
    else:                
        raise ValueError(f"●→INVALID MESSAGE TYPE RECEIVED: {response['type']}")
    

'''Response Types'''
types ={
    "msg": incoming_message,
    "con": online_user,
    "sys": system
}