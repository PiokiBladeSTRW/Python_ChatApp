'''Chooses the array of clients who'll receive the data to be broadcasted'''

'''Global Broadcasts'''
def every(clientSock, destination:str, state:object):
    rC = list(state.sock_user)
    if(clientSock in state.sock_user):
        rC.remove(clientSock)

    print("\n->", rC)
    return tuple(rC)

'''Room Broadcasts'''
def room(clientSock, destination:str, state:object): 
    rC = list(state.rooms[destination[2::]])
    rC.remove(clientSock)

    return tuple(rC)

'''User Alert'''
def user(clientSock, destination:str, state:object): 
    #For userAlerts destination is modified in Main
    return (clientSock,)

'''DM Broadcasts'''
def direct(destination:str, state:object): 
    if(destination not in state.user_sock):
        return None
    
    return (state.user_sock[destination],)


'''-------------------------------------'''


'''Parse Destination to determine Receivers'''
def parse_destination(clientSock, destination:str, state:object):
    if(destination[:2] in dest):
        data = dest[destination[:2]](clientSock, destination, state)
        return data
    else:
        data = direct(destination, state)
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