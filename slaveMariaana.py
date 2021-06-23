import socket
import struct
import time
import base64
import url
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
IS_ALL_GROUPS = True
ServerLocal = '0.0.0.0'
Port = 8000
User = 'root'
#Send

def __init__(self):
    #fazer dic user, pass
    #Parte do servidor
    self.serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criar socket
    self.serverSocket.connect((ServerLocal, Port))

    #MULTICAST
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # socket UDP
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((MCAST_GRP, MCAST_PORT))
    self.mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)




#Receive
def receive(self):
    #token pass
    #ideia: pode ser um boolean com vdd encontrou pass ou não.
    if IS_ALL_GROUPS:
        # on this port, receives ALL multicast groups
        self.sock.bind(('', MCAST_PORT))
    else:
        # on this port, listen ONLY to MCAST_GRP
        self.sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
    # For Python 3, change next line to "print(sock.recv(10240))"
        print(self.sock.recv(10240))


def send(self, token):
    token = base64.encodebytes(('%s:%s' % (User, password)).encode()).strip()
    lines = 'GET / HTTP/1.1\nHost: %s\nAuthorization: Basic %s\n\n' % ( ServerLocal, token.decode()) #linha q precisa enviar na mensagem
    self.server_sock.send(lines.encode('utf-8'))


def generatePassword(self):






while True:
    print("all your base are belong to us")
    time.sleep(1)
