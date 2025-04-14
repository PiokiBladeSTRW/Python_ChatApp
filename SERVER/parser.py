'''Handle DMs'''
def msg(clientSock:object,response:dict, state:object): 
    #Room
    if(response['receiver'].startswith('/r')):
        room = response['receiver'][2::]

        if(room not in state.rooms): 
            payload = dumps({'content': "[INVALID ROOM]", 'type':"sys"})
            return ('/s', payload, state)
        
        if(clientSock not in state.rooms[room]):                    
            state.rooms[room].append(clientSock)

        response.pop('receiver')
        response['sender'] = f"[{room}] {response['sender']}"

        return (f'/r{room}', dumps(response), state)
    
    #DM

    receiver = response.pop('receiver')
    return (receiver, dumps(response), state)

'''Handle Log In Messages'''
def usr(clientSock:object,response:dict, state:object): 
    state.user_sock[response['sender']] = clientSock
    state.sock_user[clientSock] = response['sender']

    return ('/.', dumps(response), state)

'''Handle System Messages'''
def sys(clientSock:object,response:dict, state:object):  
    content = response['content']   

    if(content == '/e'):
        return ('*', '/e', state)    #Special as disconnection is handled by async

    elif(content == '/o'):    
        data = list(state.user_sock)
        data.remove(response['sender'])
        data = '\n'.join(data)

        payload = dumps({'content': data, 'type': 'sys'})        
    
    elif(content == '/r'):
        data = '\n'.join(state.rooms.keys())

        payload = dumps({'content': data, 'type': 'sys'})
    
    elif(content.startswith('/c')):                            
        data = response['content'][2::]
        state.rooms[data] = [state.user_sock[response['sender']]]

        payload = dumps({'content': f"Room {data} Is LIVE", 'type': "sys"})        
    
    return ('/s', payload, state)       

'''Handle HeartBeat Pings'''
def hbp(clientSock:object,response:dict, state:object): 
    return ('*', '/h', state)   #Special to avoid time import


'''-------------------------------------'''


'''Parse Response Received by Clients'''
def parse_response( clientSock:object, response:dict, state:object):
    if(response['type'] in types): 
        data = types[response['type']](clientSock, response, state)
        return data    
    else:
        raise Exception("●→INVALID MESSAGE TYPE RECEIVED")

'''Response Types'''
types ={
    "msg": msg,
    "usr": usr,
    "sys": sys,
    'hbp': hbp,
}

from json import dumps


'''-------------------------------------'''


'''
RETURN FORMAT: (DESTINATION, PAYLOAD, STATE)
    RECEIVER: 
        '/.'     : All Online
        '/r--'  : All in a Room        
        '/s'    : User Alert   
        '<user>': Specific Username
        '*'     : Special Case, Need Handling
        None    : No Sending Data         
'''

# Try if(dataSend.get('receiver')): print(dataSend) to ensure there aren't useless packets being transferred