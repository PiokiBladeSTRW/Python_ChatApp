
''' This code Manages Display. Any Pieces of Strings can be formatted here'''
'''PAYLOAD: (timestamp, sender, content)'''

def format(payload, tags):   
    if(payload[0]): timestamp = time.strftime("%H:%M", time.localtime(float(payload[0])))

    data = []
    wrap = None

    for tag in tags:
        match tag:
            case 't': data.append(timestamp)
            case 's': data.append(payload[1])
            case 'c': data.append(payload[2])
            case 'bt': data.append(f"[{timestamp}]")
            case 'cl': data.append(':')
            case 'a': data.append(">")
            case 'n': data.append("\n")
            
            case 'A': wrap = ('<', '>\n')
            case 'S': wrap = ('[', ']\n')

    message = ' '.join(data)
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