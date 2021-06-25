from server.const import PASSWORD_SIZE
import time
import socket
import base64
import string
import selectors
import argparse
import algorithm

class Slave:
    __host = '172.17.0.2'
    __port = 8000
    __slave = 8001
    __username = 'root'
    done = False
    count = 0
    
    def __init__(self, ID: int, num: int):
        #slave ID
        self.ID = ID
        
        # multicast socket for communication between slaves
        self.socket_slave = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket_slave.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket_slave.bind(('', self.__slave))
        self.socket_slave.setblocking(False)
        
        # socket for communication with server
        self.socket_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_main.connect((self.__host, self.__port))
        self.socket_main.setblocking(False)
        
        # selector fot both sockets
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.socket_slave, selectors.EVENT_READ, self.recvSlave)
        self.selector.register(self.socket_main, selectors.EVENT_READ, self.recv)
        
        # chats used to make the password
        self.chars = string.ascii_letters + string.digits
        # Number of Slaves
        self.offset = num         
        
    
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
        self.socket_main.send(request.encode('utf-8'))
        
        if self.count == 8:
            time.sleep(1.5)
            self.count = 0
        

    def run(self, _timeout = 0):
        pswd = "a" * PASSWORD_SIZE
        while not self.done:
            self.guess(pswd)
            pswd = algorithm.getNext(self.chars, self.offset, self.ID, pswd)
            print(pswd)
            event = self.selector.select(timeout=_timeout)
            for key,mask in event:
                socket = key.fileobj
                callback = key.data
                callback(socket)
        self.sendSlave(self.socket_slave, self.done)


    def recv(self, socket):
        result = socket.recv(1024)
        try:
            result = result.decode('utf-8')
            result.split("\n")[-3]
        except:
            print("its good")
            self.done = True
            
    def recvSlave(self, socket):
        #resultado = Protocolo.recv(socket)
        #if resultado[type] == "NonAuthorized":
        #   pass
        #else if resultado[type] == "Done":
        #   pass
        #else:
        #   print(wrong)
        pass
    
    def sendSlave(self, socket: socket, result: bool):
        if result:
            #message = Protocolo.donemessage(socket)
            pass
        else:
            #message = Protocolo.nonauthorized(socket)
            pass
        #Protocolo.send(socket, message)
        pass
        

def main(secret):
    s = Slave(0, 1)
    s.run()   


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Authentication Server')
    parser.add_argument('-s', dest='secret', type=str, help='Http Pass', default="a")
    args = parser.parse_args()
    main(args.secret)
