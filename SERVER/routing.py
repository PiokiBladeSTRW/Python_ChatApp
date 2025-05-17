#Header
from server_state import state

def every(clientSock)-> tuple:
    '''Global Broadcasts'''

    rC = list(state.sock_uuid)
    if(clientSock in state.sock_uuid):
        rC.remove(clientSock)

    return tuple(rC)


def room(clientSock, destination:str)-> tuple: 
    '''Room Broadcasts'''

    rC = list(state.room_sock[destination])
    if(clientSock in state.room_sock[destination]):
        rC.remove(clientSock)

    return tuple(rC)


def user(clientSock)-> tuple: 
    '''User Alert'''
    return (clientSock,)


def direct(destination:str)-> tuple: 
    '''DM Broadcasts'''
    if(destination not in state.uuid_sock):
        return None    
    
    return (state.uuid_sock[destination],)


'''-------------------------------------'''


'''Parse Destination to determine receiver_ids and return an array of ids'''
def parse_destination(clientSock, destination:str) -> tuple:

    if(destination == '/.'): return every(clientSock)
    if(destination == '/s'): return user(clientSock)
    if(destination.startswith('room_')): return room(clientSock, destination)
    if(destination.startswith('user_')): return direct(destination)