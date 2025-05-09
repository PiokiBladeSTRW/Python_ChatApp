'''Chooses the array of clients who'll receive the data to be broadcasted'''
#Header
from server_state import state

'''Global Broadcasts'''
def every(clientSock):
    rC = list(state.sock_uuid)
    if(clientSock in state.sock_uuid):
        rC.remove(clientSock)

    return tuple(rC)

'''Room Broadcasts'''
def room(clientSock, destination:str): 
    rC = list(state.room_sock[destination[2::]])
    rC.remove(clientSock)    

    return tuple(rC)

'''User Alert'''
def user(clientSock): 
    return (clientSock,)

'''DM Broadcasts'''
def direct(destination:str): 
    if(destination not in state.uuid_sock):
        return None    
    
    return (state.uuid_sock[destination],)


'''-------------------------------------'''


'''Parse Destination to determine receiver_ids'''
def parse_destination(clientSock, destination:str):

    if(destination == '/.'): return every(clientSock)
    if(destination == '/s'): return user(clientSock)
    if(destination.startswith('room_')): return room(clientSock, destination)
    if(destination.startswith('user_')): return direct(destination)

'''Return Type: (receiving clients)
   None Return -> Invalid Destination
'''