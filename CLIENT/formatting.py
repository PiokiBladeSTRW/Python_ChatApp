
''' This code Manages Display. Any Pieces of Strings can be formatted here'''
'''DATA: (timestamp, sender, content)'''

def format(data:tuple, tags:tuple):   
    if(data[0]): timestamp = time.strftime("%H:%M", time.localtime(float(data[0])))
    
    msg = []
    wrap = None

    for tag in tags:
        match tag:
            case 't': msg.append(timestamp)
            case 's': msg.append(data[1])
            case 'c': msg.append(data[2])
            case 'bt': msg.append(f"[{timestamp}]")
            case 'cl': msg.append(':')
            case 'a': msg.append(">")
            
            case 'A': wrap = ('<', '>')
            case 'S': wrap = ('[', ']')

    message = ' '.join(msg)
    if(wrap): message = f"{wrap[0]} {message} {wrap[1]}"

    return message

import time

'''TAGS:

t: TimeStamp
s: Sender
c: Content

bt: Bracketed Timestamp []
cl: Colon :
a: Angle bracket >
n: Manual New Line \n       [Wraps have auto New Line]

A: Angle Bracket Cover <>
S: Square Brackets []

[Capitals Wrap the Whole Message]
'''