import json
import secrets
import hashlib
import uuid
from server_state import state

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

class authPayload(BaseModel):
    username: str
    password: str
    email: str = ''

chatApp = FastAPI()

# Authentication
@chatApp.post('/login')
def login(credentials: authPayload):

    if(credentials.username in state.uuidsFile):
        #Hash password
        user_uuid = state.uuidsFile[credentials.username]
        salt = state.accountsFile[user_uuid]['salt']
        salted_pass = credentials.password + salt
        passwd = hashlib.sha256(salted_pass.encode()).hexdigest()        

        #Match Password
        if(passwd == state.accountsFile[user_uuid]['passwd']):  
            return {"sender_id": user_uuid}
        
    return False

@chatApp.post('/register')
def register(credentials: authPayload): 

    #Ensure Username Doesn't Exist Already
    if(credentials.username in state.uuidsFile):        
        return False

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

#Entry point to server
async def api_eventLoop():    
    config = uvicorn.Config(chatApp, "127.0.0.1", 8000)
    server = uvicorn.Server(config)
    print("API SERVER ACTIVE & LISTENING")
    await server.serve()
    