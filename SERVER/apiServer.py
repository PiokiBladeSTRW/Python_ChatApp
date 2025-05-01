import json
import secrets
import hashlib
import uuid
from server_state import state

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel


with open("accounts.json", 'r') as fileHandle:
            accountsFile = json.load(fileHandle)

with open("uuids.json", 'r') as fileHandle:
            uuidsFile = json.load(fileHandle)

class authPayload(BaseModel):
    username: str
    password: str
    email: str = ''

chatApp = FastAPI()

# Authentication
@chatApp.post('/login')
def login(credentials: authPayload):

    if(credentials.username in uuidsFile):
        #Hash password
        user_uuid = uuidsFile[credentials.username]
        salt = accountsFile[user_uuid]['salt']
        salted_pass = credentials.password + salt
        passwd = hashlib.sha256(salted_pass.encode()).hexdigest()        

        #Match Password
        if(passwd== accountsFile[user_uuid]['passwd']):  
            return {"sender_id": user_uuid}
        
    return False

@chatApp.post('/register')
def register(credentials: authPayload): 

    #Ensure Username Doesn't Exist Already
    if(credentials.username in uuidsFile):        
        return False

    #Secure the Data   
    salt = secrets.token_hex(16)
    salted_pass = credentials.password + salt
    passwd = hashlib.sha256(salted_pass.encode()).hexdigest()
    print(passwd)
    user_uuid = str(uuid.uuid4())

    return {"sender_id": user_uuid}

#Entry point to server
async def api_eventLoop():    
    config = uvicorn.Config(chatApp, "127.0.0.1", 8000)
    server = uvicorn.Server(config)
    print("API SERVER ACTIVE & LISTENING")
    await server.serve()
    