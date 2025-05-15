'''Handle and Parse errors for modular message_handling'''

import json
from server_state import state

class ErrorHandle:
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
            if(args): payload = json.dumps(
                {'command': state.system_codes[error], 'content':args, 'type': state.msgTypes['system']})
                
            else: payload = json.dumps({'command': state.system_codes[error], 'type': state.msgTypes['system']})
            
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