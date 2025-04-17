'''HANDLE AUTHENTICATION'''

#Header
import json
import hashlib
import secrets

'''Register New User'''
def reg(clientSock:object, content:dict, state:object): 
    accounts = state.read_json("accounts.json")

    #Ensure Username Doesn't Exist Already
    if(content['username'] in accounts):        
        return ('/s', json.dumps({"content": state.codes['er_Exists_username'], "type":"auth"}), state)      

    #Secure the Data   
    salt = secrets.token_hex(16)
    salted_pass = content['passwd'] + salt
    passwd = hashlib.sha256(salted_pass.encode()).hexdigest()
    
    #Store the Data
    accounts[content['username']] = {"passwd": passwd, "salt": salt}
    state.write_json("accounts.json", accounts)

    #Update Server Data
    state.user_sock[content['username']] = clientSock
    state.sock_user[clientSock] = content["username"]

    #Return Confirmation
    return ('/s', True, state)

'''Log in to already made Account'''
def log(clientSock:object, content:dict, state:object):
    accounts = state.read_json("accounts.json") 

    #Log In
    if(content['username'] in accounts):
        #Hash password
        salt = accounts[content['username']]['salt']
        salted_pass = content['passwd'] + salt
        passwd = hashlib.sha256(salted_pass.encode()).hexdigest()

        #Match Password
        if(passwd== accounts[content['username']]['passwd']):   

            #Update Server Data
            state.user_sock[content['username']] = clientSock
            state.sock_user[clientSock] = content["username"]

            return ('/s', True, state)
        
    return ('/s', json.dumps({"content": state.codes['er_Invalid_login'], "type":"auth"}), state)


'''Relog to currently Active Account'''
def relog(clientSock:object, content:dict, state:object):
    accounts = state.read_json("accounts.json")
    
    username = content['username']
    if(accounts[username]['passwd'] == content['passwd']):
        return ('*', '/relog', state)

    return ('/s', json.dumps({"content": state.codes['er_Invalid_login'], "type":"auth"}), state)

'''-------------------------------------'''


'''Decide what to do with current case'''
def parse_authentication(clientSock:object, content:dict, state:object):
    match content['action']:
        case 'reg': return reg(clientSock, content, state)
        case 'log': return log(clientSock, content, state)
        case 'relog': return relog(clientSock, content, state)