'''Handle and Parse errors for modular message_handling'''

import json

class message_error_handler:
    def __init__(self):
        self.error_list = []

    '''Error Handling'''
    def error_handle(self, condition:bool, error:str,  state: object) -> tuple:
        '''Key States whether or not the 'Error' is a Code or Not'''
        if(condition):
            payload = json.dumps({'content': state.codes[error], 'type': "sys"})
            return('/s', payload, state)
        
        return None

    def parse_error(self) -> list:
        data = [x for x in self.error_list if x != None]
        self.error_list = []
        return data

    # Used by room related commands especially Invite and Admin
    def common_room_errors(self, room:str, uuid:str, user_uuid:str, state:object) -> list:
        
        self.error_list.append( self.error_handle(room not in state.room_socks, 'er_Invalid_room', state) )

        self.error_list.append( self.error_handle(uuid not in state.uuid_sock, 'user_exit', state) )

        self.error_list.append( self.error_handle(user_uuid not in state.roomsFile[room]['admins'], 'er_Not_admin' , state))

        #Errors Caught:
        return self.parse_error()