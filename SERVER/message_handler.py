'''Handle Incoming Messages (Bring about Required Changes) and Prepare data for Broadcast to Require Reciepents'''

#Header
import json

import auth

'''Handle Messages [DMs and Rooms]'''
def handle_messages(clientSock:object,response:dict, state:object): 
    
    #Room
    if(response['receiver'].startswith('/r')):
        room = response['receiver'][2::]

        # Invalid Room
        if(room not in state.rooms): 
            payload = json.dumps({'content': state.codes['er_Invalid_room'], 'type':"sys"})
            return ('/s', payload, state)
        
        # Not a Member of Room
        if(not (clientSock in state.rooms[room] or clientSock in state.room_invites[room])):
            payload = json.dumps({'content': state.codes['not_room_member'], "type":"sys"})
            return ('/s', payload, state)

        
        # If New Member
        if(clientSock in state.room_invites[room]):
            state.room_invites[room].remove(clientSock)

            state.rooms[room].append(clientSock)
            state.sock_room[clientSock] = room
            response['sender'] = f"New Member! {response['sender']} Joined\n[{room}] {response['sender']}"

        else:                    
            response['sender'] = f"[{room}] {response['sender']}"

        response.pop('receiver')

        return (f'/r{room}', json.dumps(response), state)
    
    #DM
    receiver = response.pop('receiver')
    return (receiver, json.dumps(response), state)

'''Handle System Messages'''
def system(clientSock:object,response:dict, state:object):  
    content = response['content']   

    if(content == '/e'):
        return ('*', '/exit', state)    #Special as disconnection is handled by async

    elif(content == '/o'):    
        data = list(state.user_sock)
        data.remove(response['sender'])
        data = '\n'.join(data)

        payload = json.dumps({'content': data, 'type': 'sys'})        
    
    elif(content == '/r'):
        data = '\n'.join(state.rooms.keys())

        payload = json.dumps({'content': data, 'type': 'sys'})

    elif(content.startswith('/i')):
        data= content[2::].split(';')
        room, username= data[0], data[1]


        if(room not in state.rooms):
            payload = json.dumps({"content": state.code['er_Invalid_room'], "type": "sys"})

        elif(username not in state.user_sock):
            payload = json.dumps({"content": state.codes['user_exit'], "type": "sys"})
        
        elif(username in state.rooms[room]):
            payload = json.dumps({"content": f"{username} already in {room}", "type":"sys"})
        else:        
            state.room_invites[room].append(state.user_sock[username])

            payload = json.dumps({"content": f"{room} has sent an Invitation", "type":"sys"})
            return (username, payload, state)
        
    
    elif(content.startswith('/c')):                            
        data = content[2::]

        state.rooms[data] = [state.user_sock[response['sender']]]
        state.room_invites[data] = []
        state.sock_room[clientSock] = data        

        payload = json.dumps({'content': f"Room {data} Is LIVE", 'type': "sys"})        
    
    return ('/s', payload, state)       

'''Handle HeartBeat Pings'''
def heartbeats(clientSock:object,response:dict, state:object): 
    return ('*', '/hbp', state)   #Special to avoid time import

'''Handle AUTHENTICATION'''
def authentication(clientSock:object,response:dict, state:object):
    content = response['content']
    '''Content Format: {Action: <>, Username: <>, Passwd: <>}'''
    
    #Relog
    if(content['username'] in state.user_sock): 
        content['action'] = 'relog'

    #Data is a List    
    data= auth.parse_authentication(clientSock, content, state)

    #Relog
    if(data[0] == '*'):
        return data
    
    #Succesful
    elif(data[1]== True):
        return ('*', '/logged', state)
      
    return data


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
    "msg": handle_messages,
    "sys": system,
    'hbp': heartbeats,
    'auth': authentication
}


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