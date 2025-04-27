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
    
    '''
        Types of System Codes:
        Special Actions : More action than just display [Can be of Various Types]
        Argumented      : Has Arguments
        Default         : Just Display
    '''
    if(response.get('command')):

        # ARGUMENTED
        argument_codes = (state.system_codes['new_room_member'], state.system_codes['room_live'],
                          state.system_codes['room_invite'], state.system_codes['member_admin'])
        
        if(response['command'] in argument_codes):
            args = response['content']            
            disp_msg = state.sys_code_msg[response['command']].format(*args)

            '''As of now there's only Room Commands being Argumented. Hence no extra Ifs'''
            data = ('', f"[{args[0]}] {{System}}", disp_msg)

        #SPECIAL      
        if(response['command'] == state.system_codes['user_exit']):
            # User Exit
            data = ('', response['content'], state.sys_code_msg[response['command']])
            print(formatting.format(data, ('s', 'c', 'S')))

            # Reset Receiver if exited user was the Receiver
            if(state.receiver == response['content']):
                state.receiver_change('')                
            return state

        if(response['command'] in (state.system_codes['er_Not_room_member'], state.system_codes['er_Room_exists'])):
            #Receiver Change
            state.receiver_change('')  
            data= ('', '{System}', state.sys_code_msg[response['command']])
    else:    
        data = ('', '{System}', response['content']) 

    #  Sender ({System}) : Message
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