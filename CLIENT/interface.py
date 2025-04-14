'''Handle Default Messages'''
def msg(response:dict, state:dict): 
    payload = (response['timestamp'], response['sender'], response['content'])

    # Direct Message
    if(payload[1] == state['receiver']): 
        print(formatting.format(payload, ('bt', 'a', 'c', 'n')))  

    # Room Message
    elif(payload[1].startswith('[')):
        print(formatting.format(payload, ('bt', 's', 'cl', 'c', 'n')))

    # Incoming Message
    else:
        print(formatting.format(payload, ('s', 'cl', 'c', 'A')))

    return state

'''Handle User Loggings'''
def usr(response:dict, state:dict):
    payload = ('', response['sender'], "is ONLINE")
    print(formatting.format(payload, ('s', 'c', 'S')))

    return state

'''Handle System Messages'''
def sys(response:dict, state:dict): 
    if(response['content'] == '/e'):
        payload = ('', response['sender'], 'is OFFLINE')
        print(formatting.format(payload, ('s', 'c', 'S')))

        if(state['receiver'] == response['sender']):
            state['receiver'] == ''
    
    else:    
        payload = ('', '{System}', response['content'])
        print(formatting.format(payload, ('s', 'cl', 'c')))
    
    return state
    

'''-------------------------------------'''


'''Handle Responses'''
def parse_response(response:dict, state:dict): 
    if(response['type'] in types): 
        data = types[response['type']](response, state)
        return data
    

'''Response Types'''
types ={
    "msg": msg,
    "usr": usr,
    "sys": sys
}

import formatting