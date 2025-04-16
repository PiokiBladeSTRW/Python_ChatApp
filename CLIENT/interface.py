'''Handle (bring about requried changes) and Display Incoming Data from Server'''

#Header
import formatting

'''Handle Default Messages'''
def incoming_message(response:dict, state:object): 
    data = (response['timestamp'], response['sender'], response['content'])

    # Direct Message
    if(data[1] == state.receiver): 
        print(formatting.format(data, ('bt', 'a', 'c', 'n')))  

    # Room Message
    elif(data[1].startswith('[')):
        print(formatting.format(data, ('bt', 's', 'cl', 'c')))

    # Incoming Message
    else:
        print(formatting.format(data, ('s', 'cl', 'c', 'A')))

    return state

'''Handle User Loggings'''
def online_user(response:dict, state:object):
    data = ('', response['sender'], "is ONLINE")
    print(formatting.format(data, ('s', 'c', 'S')))

    return state

'''Handle System Messages'''
def system(response:dict, state:object): 
    if(response['content'] == '/e'):
        data = ('', response['sender'], 'is OFFLINE')
        print(formatting.format(data, ('s', 'c', 'S')))

        if(state.receiver == response['sender']):
            state.receiver = ''

        return state

    elif(response['content'] == '/r1'): 
        data = ('', '{System}', "OLD SESSION LIVE; FORCE CLOSING..")

    elif(response['content'] == '/r2'): 
        data = ('', '{System}', "SUCCESSFUL RELOG!")
    
    else:    
        data = ('', '{System}', response['content']) 

    print(formatting.format(data, ('s', 'cl', 'c')))    
    return state
    

'''-------------------------------------'''


'''Handle Responses'''
def parse_response(response:dict, state:object): 
    if(response['type'] in types): 
        state = types[response['type']](response, state)
        return state
    else:
        raise Exception("●→INVALID MESSAGE TYPE RECEIVED")
    

'''Response Types'''
types ={
    "msg": incoming_message,
    "usr": online_user,
    "sys": system
}