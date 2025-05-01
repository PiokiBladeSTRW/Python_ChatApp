#Header
import requests
import maskpass

legal_char = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890@#"

def login() -> str:   
    '''Takes credentials as Input from user and sends request to server to verify them
    Returns: uuid if Succesful ; False if server denies request''' 

    # Username Entry
    username = input("\nENTER USERNAME: ").strip()
    if(not all(c in legal_char for c in username)):
        print("ILLEGAL CHARACTERS")
        return False

    # Password Entry
    password = maskpass.askpass(prompt="ENTER PASSWORD: ", mask='*')   
     
    # Server Request
    content = {"username": username, "password": password}
    authRes = requests.post("http://127.0.0.1:8000/login", json=content).json() 

    if(type(authRes)==dict):        
        return authRes['sender_id']

    return False

def register(): 
    '''Takes credentials as Input from user and sends request to server to create an account
    Returns: uuid if Succesful ; False if server denies request'''
    
    def is_invalid_email(email):
        if('@' not in email):
            return True
        return False 
    
    # Username Entry
    username = input("\nENTER USERNAME: ").strip()
    if(not all(c in legal_char for c in username)):
        print("ILLEGAL CHARACTERS")
        return False

    # Password Entry
    password = maskpass.askpass(prompt="ENTER PASSWORD: ", mask='*')    
    
    # Email Entry
    email = input("ENTER EMAIL: ")
    if(is_invalid_email(email)): 
        print("INVALID EMAIL")
        return False

    # Server Request
    content = {"username": username, "password": password, "email": email}
    authRes = requests.post("http://127.0.0.1:8000/register", json=content).json() 

    if(type(authRes)==dict):        
        return authRes['sender_id']

    return False


'''-------------------------------------'''

 
'''Start the Process by determining New or Old account'''
def start_auth() -> dict:
    ch = input("0: Login to Account\n1: Register an Account\n>")

    while True:       
        if (ch == '0'): user_uuid = login()
        elif (ch == '1'): user_uuid = register()
        else: continue

        if (not user_uuid): 
            print("INVALID LOGIN")
            continue

        return user_uuid