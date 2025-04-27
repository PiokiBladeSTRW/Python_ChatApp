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

        # If New Member Joined
        if(data[2] == 105):       
            data = (response['timestamp'], f"[{room}] {username}", state.system_codes[105])
            print(formatting.format(data, ('bt', 's', 'c')))

        # Direct Room Broadcast
        elif(room == state.receiver[2::]):
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
    
    '''Handle System Code Messages'''
    if(response.get('command')):
        '''
        Types of System Codes:
        Special Actions : More action than just display [Can be of Various Types]
        Argumented      : Has Arguments
        Default         : Just Display
        '''
        print(response['command'])
        # ARGUMENTED
        if(response['command'] in (104, 105, 106, 107)):
            args = response['content']
            print(args)
            disp_msg = state.sys_code_msg[response['command']].format(*args)

            '''As of now there's only Room Commands being Argumented. Hence no extra Ifs'''
            data = ('', f"[{args[0]}] {{System}}", disp_msg)

        #SPECIAL      
        if(response['command'] == 101):
            # User Exit
            data = ('', response['content'], 'is OFFLINE')
            print(formatting.format(data, ('s', 'c', 'S')))

            # Reset Receiver if exited user was the Receiver
            if(state.receiver == response['content']):
                state.receiver_change('')                
            return state

        if(response['command'] in (204,205)):
            #Receiver Change
            state.receiver_change('')  
            data= ('', '{System}', state.sys_code_msg[response['command']])
    else:    
        data = ('', '{System}', response['content']) 

    #  Sender ({System}) : Message
    print(data)
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