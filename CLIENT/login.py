'''Handle the Entire Log-in Process'''

#Header
import maskpass
legal_char = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890@#"

'''Input Credentials from User:'''
def credentials_input(action):
    def is_invalid_email(email):
        if('@' not in email):
            return True
        return False

    username = input("ENTER USERNAME: ").strip()
    if(not all(c in legal_char for c in username)):
        print("ILLEGAL CHARACTERS")
        return None

    passwd = maskpass.askpass(prompt="ENTER PASSWORD: ", mask='*')
    email = input("ENTER EMAIL: ")
    if(is_invalid_email(email)): 
        print("INVALID EMAIL")
        return None
    
    content = {"action": action, "username": username, "passwd": passwd, "email": email}

    return content


'''Start the Process by determining New or Old account'''
def start_auth():
    while True:
        ch = input("0: Login to Account\n1: Register an Account\n>")

        if(ch=='0'):
            content = credentials_input('log')
        elif(ch=='1'):
            content = credentials_input('reg')
        else:            
            continue

        if(content==None):
            continue

        return content

'''
RETURN FORMAT:
        {
        "action": action
        "username": username,
        "passwd": passwd,
        }
'''