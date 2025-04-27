'''Handle and Parse errors for modular message_handling'''

import json

class CatchError:
    def __init__(self):
        self.error_list = []

    '''Error Handling'''
    def error_handle(self, condition:bool, error:str, args:tuple, state: object) -> tuple:
        '''Key States whether or not the 'Error' is a Code or Not'''
        if(condition):
            payload = json.dumps({'command': state.system_codes[error], 'content':args, 'type': "sys"})
            return('/s', payload, state)
        
        return None

    def parse_error(self) -> tuple:
        data = tuple(x for x in self.error_list if x != None)
        self.error_list = []
        return data
    
    def multiple_error_handle(self, possible_errors:dict[str,tuple], state:object) -> tuple:
        for error in possible_errors:
            self.error_list.append(self.error_handle(possible_errors[error][0], error, possible_errors[error][1], state))

        return self.parse_error()
    
''' Mostly multiple_error_handle is used. As singular error handling requires an unnecessary variable in main_module'''