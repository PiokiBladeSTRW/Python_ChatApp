from server_state import state
import auth.auth_handle as auth_handle
import message.api_commands as api_cmd

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

chatApp = FastAPI()

# Authentication
class authPayload(BaseModel):
    username: str
    password: str
    email: str = ''

@chatApp.post('/login')
def login(credentials: authPayload) -> dict:
    return auth_handle.login(credentials)    

@chatApp.post('/register')
def register(credentials: authPayload) -> dict: 
    return auth_handle.register(credentials)

# System

@chatApp.get("/uuid_to_name/{uuid}")
def uuid_to_name(uuid: str) -> dict:    
    if(uuid in state.accountsFile):
        username = state.accountsFile[uuid]['username']
        return {"content": username}
    
    elif(uuid in state.roomsFile):
        room_name = state.roomsFile[uuid]['name']
        return {"content": room_name}
    
    raise HTTPException(404, f"Invalid UUID {uuid}")

@chatApp.get("/name_to_uuid/{name}")
def name_to_uuid(name: str) -> dict:
    
    if(name in state.username_uuid):
        return {"content": state.username_uuid[name]}
    
    if(name in state.roomName_roomUuid)    :
        return {"content": state.roomName_roomUuid[name]}
    
    return {"content": 0}

# Commands
     


# Check for Server being online
@chatApp.get("/")
def online() -> bool:
    return True

#Entry point to server
async def api_eventLoop():   
    host, port = "127.0.0.1" , 8000
    config = uvicorn.Config(chatApp, host, port)
    server = uvicorn.Server(config)
    
    state.log(f"API Server Active & Listening at {host}:{port}")
    print("API SERVER ACTIVE & LISTENING")
    await server.serve()
    