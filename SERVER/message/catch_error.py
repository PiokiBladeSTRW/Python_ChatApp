'''Handle and Parse errors for modular message_handling'''

import json

class CatchError:
    def __init__(self):
        self.error_list = []

    '''Error Handling'''
    def error_handle(self, condition:bool, error:str,  state: object) -> tuple:
        '''Key States whether or not the 'Error' is a Code or Not'''
        if(condition):
            payload = json.dumps({'content': state.system_codes[error], 'type': "sys"})
            return('/s', payload, state)
        
        return None

    def parse_error(self) -> tuple:
        data = tuple(x for x in self.error_list if x != None)
        self.error_list = []
        return data
    
    def multiple_error_handle(self, error_condition:dict[str,bool], state:object) -> tuple:
        for error in error_condition:
            self.error_list.append( self.error_handle(error_condition[error], error, state) )

        return self.parse_error()
    
    