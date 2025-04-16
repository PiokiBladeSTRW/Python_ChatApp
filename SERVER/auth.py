'''HANDLE AUTHENTICATION'''

'''Register New User'''
def reg(content:dict, state:object): 
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)
        if(content['username'] in accounts):
            return ('/s', json.dumps({"content": "USERNAME EXISTS", "type":"auth"}), state)
        accounts[content['username']] = {"passwd": content['passwd']}
    
    with open('accounts.json', 'w') as f:
        json.dump(accounts, f)

    return ('/s', json.dumps({"content": True, "type":"auth"}), state)

'''Log in to already made Account'''
def log(content:dict, state:object):
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)

    if(content['username'] in accounts):
        if(accounts[content['username']]['passwd'] == content['passwd']):
            return ('/s', json.dumps({"content": True, "type":"auth"}), state)
        
    return ('/s', json.dumps({"content": False, "type":"auth"}), state)


'''-------------------------------------'''


'''Decide what to do with current case'''
def parse_authentication(content:dict, state:object):
    match content['action']:
        case 'reg': return reg(content, state)
        case 'log': return log(content, state)

import json