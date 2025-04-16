'''Handle the Entire Log-in Process'''

'''Input Data from User:'''
def credentials_input(action):
    username = input("ENTER USERNAME: ").strip()
    passwd = input("ENTER PASSWORD: ")
    
    content = {"action": action, "username": username, "passwd": passwd}

    return content


'''Start the Process by determining New or Old account'''
def begin_process():
    while True:
        ch = input("0: Login to Account\n1: Register an Account\n>")

        if(ch=='0'):
            content = credentials_input('log')
        elif(ch=='1'):
            content = credentials_input('reg')
        else:            
            continue

        return content

'''RETURNS CONTENT
CONTENT = {
        "action": action
        "username": username,
        "passwd": passwd,
            }
'''