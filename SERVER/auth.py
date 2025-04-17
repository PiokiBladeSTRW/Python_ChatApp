'''HANDLE AUTHENTICATION'''

#Header
import json

'''Register New User'''
def reg(clientSock:object, content:dict, state:object): 
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)

        #Ensure Username Doesn't Exist Already
        if(content['username'] in accounts):
            return ['/s', {"content": state.codes['er_Exists_username'], "type":"auth"}, state]
        
        accounts[content['username']] = {"passwd": content['passwd']}
    
    #Store Data
    with open('accounts.json', 'w') as f:
        json.dump(accounts, f)

    #Update Server Data
    state.user_sock[content['username']] = clientSock
    state.sock_user[clientSock] = content["username"]

    #Return Confirmation
    return ('/s', {"content": True, "type":"auth"}, state)

'''Log in to already made Account'''
def log(clientSock:object, content:dict, state:object):
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)

    #Log In
    if(content['username'] in accounts):
         if(accounts[content['username']]['passwd'] == content['passwd']):            
            #Update Server Data
            state.user_sock[content['username']] = clientSock
            state.sock_user[clientSock] = content["username"]

            return ('/s', {"content": True, "type":"auth"}, state)
        
    return ['/s', {"content": state.codes['er_Invalid_login'], "type":"auth"}, state]

'''Relog to currently Active Account'''
def relog(clientSock:object, content:dict, state:object):
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)
    
    username = content['username']
    if(accounts[username]['passwd'] == content['passwd']):
        return ('*', '/relog', state)

    return ['/s', {"content": state.codes['er_Invalid_login'], "type":"auth"}, state]

'''-------------------------------------'''


'''Decide what to do with current case'''
def parse_authentication(clientSock:object, content:dict, state:object):
    match content['action']:
        case 'reg': return reg(clientSock, content, state)
        case 'log': return log(clientSock, content, state)
        case 'relog': return relog(clientSock, content, state)