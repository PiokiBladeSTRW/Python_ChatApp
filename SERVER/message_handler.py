'''Handle Incoming Messages (Bring about Required Changes) and Prepare data for Broadcast to Require Reciepents'''

#Header
import json
import auth

er_lst= []

'''Error Handling'''
def error_handle(condition, error:str,  state: object):
    '''Key States whether or not the 'Error' is a Code or Not'''
    if(condition):
        payload = json.dumps({'content': state.codes[error], 'type': "sys"})
        return('/s', payload, state)
    
    return None

'''Handle Messages [DMs and Rooms]'''
def handle_messages(clientSock:object,response:dict, state:object): 
    def room_handle(room):

        #Invalid Room
        er_lst.append( error_handle(room not in state.room_socks, 'er_Invalid_room',  state) )

        #Not a Member AND not Invited [De Morgan's Law]
        er_lst.append(error_handle(not(clientSock in state.room_socks[room] or clientSock in state.room_invites[room]),
                                   'not_room_member', state))

        #If Error caught, return it
        data = [x for x in er_lst if x != None]
        if(data): return data[0]
        er_lst = []


        response.pop('receiver') 
        username = state.uuid_user(response['sender'])
        response['sender'] = f"[{room}] {username}"
                
        # If New Member
        if(clientSock in state.room_invites[room]):
            state.room_invites[room].remove(clientSock)

            state.room_socks[room].append(clientSock)
            state.sock_rooms[clientSock] = room

            state.roomsFile[room]['members'].append(state.sock_uuid[clientSock])
            state.accountsFile[state.sock_uuid[clientSock]]['rooms'].append(room)

            response['sender'] = f"New Member! {username} Joined\n{response['sender']}"

        return (f'/r{room}', json.dumps(response), state)

    def dm_handle():
        response['sender'] = state.uuid_user(response['sender'])
        receiver = state.uuidsFile[response.pop('receiver')]
        return (receiver, json.dumps(response), state)
    
    if(response['receiver'].startswith('/r')):
       return room_handle(response['receiver'][2::])

    return dm_handle()

'''Handle System Messages'''
def system(clientSock:object, response:dict, state:object):  
    def common_room_errors(room, username):
        er_lst.append( error_handle(room not in state.room_socks, 'er_Invalid_room', state) )

        er_lst.append( error_handle(username not in state.uuidsFile, 'user_exit', state) )

        er_lst.append( error_handle(response['sender'] not in state.roomsFile[room]['admins'], 'er_Not_admin' , state))

        #Errors Caught:
        data = [x for x in er_lst if x !=None]
        if(data): return data[0]
        
        er_lst = []        
        return None

    #Main Code
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

        data = common_room_errors(room, username)
        if(data): return data

        uuid = state.uuidsFile[username]

        if(state.uuid_sock[uuid] in state.room_socks[room] or state.uuid_sock[uuid] in state.room_invites[room]):
            payload = json.dumps({"content": f"{username} already in {room}", "type":"sys"})

        else:        
            state.room_invites[room].append(state.uuid_sock[uuid])
            payload = json.dumps({"content": f"{room} has sent an Invitation", "type":"sys"})            
            return (uuid, payload, state)
        
    elif(content.startswith('/a')):
        data= content[2::].split(';')
        room, username= data[0], data[1]        

        data = common_room_errors(room, username)
        if(data): return data

        uuid = state.uuidsFile[username]    
        if(uuid in state.roomsFile[room]['admins']):
            payload = json.dumps({"content": f"{username} is already an admim", "type": "sys"})

        else:     
            state.roomsFile[room]['admins'].append(uuid)            
            payload = json.dumps({"content": f"{room} has made {state.uuid_user(uuid)} an ADMIN", "type":"msg"})            
            return (f'/r{room}', payload, state)
    
    elif(content.startswith('/c')):
        room = content[2::]

        state.room_invites[room] = []        
        state.room_socks[room] = [clientSock]
        
        state.sock_rooms[clientSock].append(room)
        
        state.roomsFile[room] = {'members': [], 'admins': []}
        state.roomsFile[room]['members'].append(response['sender'])
        state.roomsFile[room]['admins'].append(response['sender'])

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
    if(content['username'] in state.uuidsFile and state.uuidsFile[content['username']] in state.uuid_sock):
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