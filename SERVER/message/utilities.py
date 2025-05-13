'''Handle and Parse errors for modular message_handling'''

import json
import time
import uuid
from server_state import state

class MessageUtility:
    def __init__(self):
        self.error_list = []

    def error_handle(self, condition:bool, error:str, args:tuple =None) -> tuple:
        '''Returns Specific Payload if the condition is true
        @params: 
            condition: Boolean value checking for error
            error: Key for error code to be sent
            args: In case the command has any parameters to transfer
        @returns: 
            Message Payload of Error if there is an Error; or None
        '''

        if(condition):
            if(args): payload = json.dumps({'command': state.system_codes[error], 'content':args, 'type': "sys"})
            else: payload = json.dumps({'command': state.system_codes[error], 'type': "sys"})
            
            return('/s', payload)
        
        return None
    
    def error_return(self):
        data = self.error_list[-1]
        self.error_list = []
        return data

    
    def multiple_error_handle(self, possible_errors:dict[str,tuple]) -> tuple:
        '''Handles Multiple Errors at once, returns the first error to appear
        @params:
            possible_errors: Dictionary with key:value -> error key : [error condition, arguments if any]
        @returns: 
            parsed error list or none
        '''

        for error in possible_errors:
            self.error_list.append(self.error_handle(possible_errors[error][0], error, possible_errors[error][1]))
            if(any(self.error_list)): break

        return self.error_return()
    
    '''------------------------------------------------------------------'''

    def encode_payload(self, command:int=None, content=None,  sender_id: str = None) -> str:
        data = {
            'command': command,
            'content': content,
            'type': 'sys',
        }
        if(sender_id): data['sender_id'] = sender_id
        return json.dumps(data)

    def modify_room(self, room_uuid:str, operation: tuple, clientSock:object=None, user_uuid:str=None, room_name:str=None):
        '''Types of Operation: (CREATE, N_JOIN, INVITE, R_INVITE, ADMIN, KICK, BAN)
        clientSock: Person using Command ;  uuid: Person on receiving End of Command
        Returning Operations: (CREATE,)'''    

        # Ran By Person Creating Server
        if('CREATE' in operation):        
            room_uuid = 'room_' + str(uuid.uuid4())

            state.room_sock[room_uuid] = []
            state.roomName_roomUuid[room_name] = room_uuid
            state.roomsFile[room_uuid] = {'name': room_name,
                                        'members': [], 
                                        'admins': [], 
                                        'invites': [], 
                                        'bans': [],
                                        'creation': time.strftime("%D", time.localtime()),
                                        'desc': ""}          
            return room_uuid

        # Ran by Person joining Server
        if('N_JOIN' in operation):
            state.room_sock[room_uuid].append(clientSock)
            state.sock_rooms[clientSock].append(room_uuid)       

            state.roomsFile[room_uuid]['members'].append(state.sock_uuid[clientSock])
            state.uuidsFile[state.sock_uuid[clientSock]]['rooms'].append(room_uuid)      
        
        # Ran by Admin Targetted to Invitee
        if('INVITE' in operation):
            state.roomsFile[room_uuid]['invites'].append(user_uuid)  

        # Ran by Person joining Server
        if('R_INVITE' in operation):
            state.roomsFile[room_uuid]['invites'].remove(state.sock_uuid[clientSock])

        # Ran by Admin Targetted to Member
        if('ADMIN' in operation):
            state.roomsFile[room_uuid]['admins'].append(user_uuid)

        # Ran by Admin Targetted to Member
        if('KICK' in operation):
            state.roomsFile[room_uuid]['members'].remove(user_uuid)
            state.uuidsFile[user_uuid]['rooms'].remove(room_uuid)

            state.sock_rooms[state.uuid_sock[user_uuid]].remove(room_uuid)
            state.room_sock[room_uuid].remove(state.uuid_sock[user_uuid])
        
        # Ran by Admin Targetted to Member
        if('BAN' in operation):
            state.roomsFile[room_uuid]['bans'].append(user_uuid)
        
        # Ran by Admin Targetted to Member
        if('UNBAN' in operation):            
            state.roomsFile[room_uuid]['bans'].remove(user_uuid)   
    

utility = MessageUtility()