import base64

def encryption(msg):
    return base64.b64encode(msg.encode())

def decryption(msg):
    return base64.b64decode(msg).decode()