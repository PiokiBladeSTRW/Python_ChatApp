''' Handle Broadcasting by making List of Receiving Clients'''

'''Global Broadcasts'''
def every(clientSock, destination:str, state:object):     
    rC = list(state.sock_user)
    rC.pop(clientSock)

    return tuple(rC)

'''Room Broadcasts'''
def room(clientSock, destination:str, state:object): 
    rC = state.rooms[destination[2::]]
    rC.pop(clientSock)

    return tuple(rC)

'''User Alert'''
def user(clientSock, destination:str, state:object): 
    #For userAlerts destination is modified in Main
    return (clientSock,)

'''DM Broadcasts'''
def dm(destination:str, state:object): 
    if(destination not in state.user_sock):
        return None
    
    return (state.user_sock[destination],)

'''Parse Destination to determine Receivers'''
def parse_destination(clientSock, destination:str, state:object):
    if(destination in dest):
        data = dest[destination](clientSock, destination, state)
        return data
    else:
        data = dm(destination, state)
        return data


'''Destinations'''
dest= {
    '/.': every,
    '/r': room,
    '/s': user
}

'''Return Type: (receiving clients)
   None Return -> Invalid Destination
'''