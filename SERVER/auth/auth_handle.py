#Header
import json
import secrets
import hashlib
import uuid
from server_state import state


def login(credentials: object) -> dict: 
    '''Verify the credentials sent are Valid'''
    if(credentials.username in state.uuidsFile):
        #Hash password
        user_uuid = state.uuidsFile[credentials.username]
        salt = state.accountsFile[user_uuid]['salt']
        salted_pass = credentials.password + salt
        passwd = hashlib.sha256(salted_pass.encode()).hexdigest()        

        #Match Password
        if(passwd == state.accountsFile[user_uuid]['passwd']):  
            return {"sender_id": user_uuid}
        
    return {"content": "Invalid Username or Password"}

def register(credentials: object) -> dict: 
    '''Create an account with given credentials if username isn't conflicting'''
    
    #Ensure Username Doesn't Exist Already
    if(credentials.username in state.uuidsFile):        
        return {"content": "The Username is Taken"}

    #Secure the Data   
    salt = secrets.token_hex(16)
    salted_pass = credentials.password + salt
    passwd = hashlib.sha256(salted_pass.encode()).hexdigest()
    print(passwd)
    user_uuid = str(uuid.uuid4())

    #Store the Data
    state.accountsFile[user_uuid] = {
        "username":credentials.username, 
        "passwd": passwd, 
        "email": credentials.email,
        "salt": salt, 
        "rooms": []                                     
        }
    state.uuidsFile[credentials.username] = user_uuid

    return {"sender_id": user_uuid}