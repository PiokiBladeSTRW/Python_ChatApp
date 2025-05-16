#Header
from session_state import state

def error_display(display_message:str) -> tuple:
    '''To avoid Redundant code; Logs, Displays and Returns Hollow Data together'''
    
    state.log(f"User Dispaly Error: {display_message}")

    print(f"{{System}}: {display_message}")
    return (None, None)