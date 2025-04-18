'''HANDLE AUTHENTICATION'''

#Header
import json
import hashlib
import secrets
import uuid

'''Register New User'''
def reg(clientSock:object, content:dict, state:object):
    #Ensure Username Doesn't Exist Already
    if(content['username'] in state.uuidsFile):        
        return ('/s', json.dumps({"content": state.codes['er_Exists_username'], "type":"sys"}), state)      

    #Secure the Data   
    salt = secrets.token_hex(16)
    salted_pass = content['passwd'] + salt
    passwd = hashlib.sha256(salted_pass.encode()).hexdigest()
    user_uuid = str(uuid.uuid4())
    
    #Store the Data
    state.accountsFile[user_uuid] = {"username":content['username'], "passwd": passwd, "salt": salt}
    state.uuidsFile[content['username']] = user_uuid

    #Update Server Data
    state.user_sock[content['username']] = clientSock
    state.sock_user[clientSock] = content["username"]

    #Return Confirmation
    return ('/s', True, state)

'''Log in to already made Account'''
def log(clientSock:object, content:dict, state:object):
    if(content['username'] in state.uuidsFile):
        #Hash password
        user_uuid = state.uuidsFile[content['username']]
        salt = state.accountsFile[user_uuid]['salt']
        salted_pass = content['passwd'] + salt
        passwd = hashlib.sha256(salted_pass.encode()).hexdigest()
        

        #Match Password
        if(passwd== state.accountsFile[user_uuid]['passwd']):   

            #Update Server Data
            state.user_sock[content['username']] = clientSock
            state.sock_user[clientSock] = content["username"]

            return ('/s', True, state)
        
    return ('/s', json.dumps({"content": state.codes['er_Invalid_login'], "type":"sys"}), state)


'''Relog to currently Active Account'''
def relog(clientSock:object, content:dict, state:object):    
    username = content['username']
    if(state.accountsFile[username]['passwd'] == content['passwd']):
        return ('*', '/relog', state)

    return ('/s', json.dumps({"content": state.codes['er_Invalid_login'], "type":"sys"}), state)

'''-------------------------------------'''


'''Decide what to do with current case'''
def parse_authentication(clientSock:object, content:dict, state:object):
    match content['action']:
        case 'reg': return reg(clientSock, content, state)
        case 'log': return log(clientSock, content, state)
        case 'relog': return relog(clientSock, content, state)