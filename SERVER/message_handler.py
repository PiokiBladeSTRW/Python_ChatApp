'''Handle Incoming Messages (Bring about Required Changes) and Prepare data for Broadcast to Require Reciepents'''

#Header
import json

import auth

'''Handle Messages [DMs and Rooms]'''
def handle_messages(clientSock:object,response:dict, state:object): 
    def room_handle(room):

        #Invalid Room
        if(room not in state.room_socks):    
            payload = json.dumps({'content': state.codes['er_Invalid_room'], 'type':"sys"})
            return('/s', payload, state)
        
        #Not a Member of Room AND not invited [De Morgan's Law]
        if(not (clientSock in state.room_socks[room] or clientSock in state.room_invites[room])):
            payload = json.dumps({'content': state.codes['not_room_member'], 'type':"sys"})
            return ('/s', payload, state)
        
        response.pop('receiver') 
        username = state.uuid_user(response['sender'])
        response['sender'] = f"[{room}] {username}"
                
        # If New Member
        if(clientSock in state.room_invites[room]):
            state.room_invites[room].remove(clientSock)

            state.room_socks[room].append(clientSock)
            state.sock_rooms[clientSock] = room

            state.roomsFile[room].append(state.sock_uuid[clientSock])
            state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room)

            response['sender'] = f"New Member! {username} Joined\n{response['sender']}"

        return (f'/r{room}', json.dumps(response), state)

    def dm_handle():
        response['sender'] = state.uuid_user(response['sender'])
        receiver = state.uuidsFile[response.pop('receiver')]
        return (receiver, json.dumps(response), state)
    
    
    if(response['receiver'].startswith('/r')):
       return room_handle(response['receiver'][2::])
    else:
        return dm_handle()

'''Handle System Messages'''
def system(clientSock:object, response:dict, state:object):  
    content = response['content']   

    if(content == '/e'):
        return ('*', '/exit', state)    #Special as disconnection is handled by async

    elif(content == '/o'):    
        data = list(state.uuidsFile)
        data.remove(state.uuids_user(response['sender']))
        data = '\n'.join(data)
        payload = json.dumps({'content': data, 'type': 'sys'})
    
    elif(content == '/r'):
        data = '\n'.join(state.room_socks.keys())
        payload = json.dumps({'content': data, 'type': 'sys'})

    elif(content.startswith('/i')):
        data= content[2::].split(';')
        room, username= data[0], data[1]
        uuid= state.uuidsFile[username]

        if(room not in state.room_socks):
            payload = json.dumps({"content": state.code['er_Invalid_room'], "type": "sys"})

        elif(uuid not in state.uuid_sock):
            payload = json.dumps({"content": state.codes['user_exit'], "type": "sys"})
        
        elif(state.uuid_sock[uuid] in state.room_socks[room] or state.uuid_sock[uuid] in state.room_invites[room]):
            payload = json.dumps({"content": f"{username} already in {room}", "type":"sys"})

        else:        
            state.room_invites[room].append(state.uuid_sock[uuid])
            payload = json.dumps({"content": f"{room} has sent an Invitation", "type":"sys"})            
            return (uuid, payload, state)
        
    
    elif(content.startswith('/c')):
        room = content[2::]

        state.room_invites[room] = []        
        state.room_socks[room] = [clientSock]
        
        state.sock_rooms[clientSock].append(room)
        
        state.roomsFile[room] = [response['sender']]
        state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room)

        payload = json.dumps({'content': f"Room {room} Is LIVE", 'type': "sys"})        
    
    return ('/s', payload, state)       

'''Handle HeartBeat Pings'''
def heartbeats(clientSock:object,response:dict, state:object): 
    return ('*', '/hbp', state)   #Special to avoid time import

'''Handle AUTHENTICATION'''
def authentication(clientSock:object,response:dict, state:object):
    content = response['content']
    '''Content Format: {Action: <>, Username: <>, Passwd: <>}'''
    
    #Relog
    if(content['username'] in state.uuidsFile):
        if(state.uuidsFile[content['username']] in state.uuid_sock): 
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