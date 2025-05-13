#Header
import requests
import maskpass

class APIClient:
    def __init__(self):
        self.legal_char = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890@#"

    def login(self) -> str:   
        '''Takes credentials as Input from user and sends request to server to verify them
        Returns: uuid if Succesful ; False if server denies request''' 

        # Username Entry
        username = input("\nENTER USERNAME: ").strip()
        if(not all(c in self.legal_char for c in username)):
            print("ILLEGAL CHARACTERS")
            return False

        # Password Entry
        password = maskpass.askpass(prompt="ENTER PASSWORD: ", mask='*')   
        
        # Server Request
        content = {"username": username, "password": password}
        authRes = requests.post("http://127.0.0.1:8000/login", json=content).json() 

        return authRes, False

    def register(self) -> str: 
        '''Takes credentials as Input from user and sends request to server to create an account
        Returns: uuid if Succesful ; False if server denies request'''
        
        def is_invalid_email(email):
            if('@' not in email):
                return True
            return False 
        
        # Username Entry
        username = input("\nENTER USERNAME: ").strip()
        if(not all(c in self.legal_char for c in username)):
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

        return authRes, username

    
    '''Start the Process by determining New or Old account'''
    def start_auth(self) -> str:
        ch = input("0: Login to Account\n1: Register an Account\n>")

        while True:       
            if (ch == '0'): authRes, user = self.login()
            elif (ch == '1'): authRes, user = self.register()
            else: 
                ch = input("0: Login to Account\n1: Register an Account\n>")
                continue
            
            # Client Side Fail
            if(not authRes): continue

            # Succesful Log-In
            if(authRes.get('sender_id')):        
                return authRes['sender_id'], user

            # Server Side Fail
            print(authRes['content'])
            continue

api_client = APIClient() 