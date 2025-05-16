'''Formats Message as required for Different Displays for Different Purposes'''

# Header
import time
time_format = "%H:%M"

def format(data:tuple, tags:tuple) -> str:   
    '''DATA: (timestamp, sender_id, content, receiver_id)'''

    # Make timestamp Readable as originally it is time.time()
    if(data[0]): timestamp = time.strftime(time_format, time.localtime( float( data[0] ) ))
    
    msg_bits = []
    wrap = None

    for tag in tags:
        match tag:
            case 't': msg_bits.append(timestamp)
            case 's': msg_bits.append(data[1])
            case 'r': msg_bits.append(data[3])
            case 'c': msg_bits.append(data[2])
            case 'bt': msg_bits.append(f"[{timestamp}]")
            case 'cl': msg_bits.append(':')
            case 'a': msg_bits.append(">")
            
            case 'A': wrap = ('<', '>')
            case 'S': wrap = ('[', ']')
    
    # Prepare final message from bits    
    final_msg = ' '.join(msg_bits)
    if(wrap): final_msg = f"{wrap[0]} {final_msg} {wrap[1]}"

    return final_msg

'''
TAGS:

t: TimeStamp
s: sender_id
c: Content

bt: Bracketed Timestamp []
cl: Colon :
a: Angle bracket >
n: Manual New Line \n       [Wraps have auto New Line]

A: Angle Bracket Cover <>
S: Square Brackets []

[Capitals Wrap the Whole Message]
'''