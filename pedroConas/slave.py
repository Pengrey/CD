import socket
import struct
import time
import base64
import cracker
import argparse
import pickle
import logging
import time
import sys
import random
from utils import dht_hash


MCAST_GRP = '224.3.29.71'
MCAST_PORT = 5007
IS_ALL_GROUPS = False
ServerLocal = '127.0.1.1'
Port = 8000
User = 'root'
#Send
class Slave:
    def __init__(self, timeout = 3, secret = None,MSize = 1 ):
        #fazer dic user, pass
        #Parte do servidor
        """
            Secalhar nao criavamos logo a socket TCP
            Primeiro trocavamos mensagens para decidir quem tinha o maior ID (Por floding no inicio que é mais fácil depois tentar por bullying?)
            Depois esse ID determinava quem se iria ligar ao HTTPServer (tipo os 3 mais pequenos que responderem)
            Os que respondiam com um Ack comecavam a trabalhar
            Se algum deles nao respondesse ou nao envia se uma mensagem de Acknowledge
            o Coordenador(Maior ID) Escolhia outro(1 ou mais) gajo para ser outro slave
            so one and so forth
            Esses 3 escolhido periodicamente informavam o coordenador do seu 'estado'
            Tipo uma lista de passes testadas ou a pedir mais ou a dizer ei descobri a pass

        self.serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #criar socket
        self.serverSocket.connect((ServerLocal, Port))
        """

        global MCAST_GRP
        global MCAST_PORT
        self.mreq = struct.pack('b',1)
        #MULTICAST
        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket UDP
        self.sockUDP.settimeout(timeout)

        #global MCAST_GRP

        self.sockUDP.bind(('', MCAST_PORT))
        group = socket.inet_aton(MCAST_GRP)
        mreq = struct.pack('4sl', group, socket.INADDR_ANY)
        self.sockUDP.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sockUDP.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_LOOP,0)
        self.done_UDP = False
        self.role = None

        #self.sock.bind(( MCAST_GRP, MCAST_PORT))

        #self.generatePassword(MSize)

        hostname = socket.gethostname()

        self.address = socket.gethostbyname(hostname)
        print("sadfas" , self.address)
        print("asdfasdfasdf" , self.sockUDP.getsockname())
        print("---" , socket.getnameinfo(self.sockUDP.getsockname(), socket.NI_NUMERICHOST | socket.NI_NUMERICSERV )[1])
        self.port = int(socket.getnameinfo(self.sockUDP.getsockname(), socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)[1])

        self.identification = dht_hash(self.address.__str__())
        self.logger = logging.getLogger(f"Slave {self.identification}")


    #Receive
    """
    def receive(self):
        global IS_ALL_GROUPS
        global MCAST_PORT
        global MCAST_GRP

        #token pass
        #ideia: pode ser um boolean com vdd encontrou pass ou não.
        if  IS_ALL_GROUPS:
            # on this port, receives ALL multicast groups
            self.sock.bind(('', MCAST_PORT))
        else:
            # on this port, listen ONLY to MCAST_GRP

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)

        while True:
        # For Python 3, change next line to "print(sock.recv(10240))"
            print(self.sock.recv(10240))
            """

    def sendPass(self, password):
        global User
        global ServerLocal
        token = base64.encodebytes((f"{User}:{password}").encode()).strip()
        lines = f"GET / HTTP/1.1\nHost: {ServerLocal}\nAuthorization: Basic {token.decode()}\n\n" #linha q precisa enviar na mensagem
        self.server_sock.send(lines.encode('utf-8'))


    def generatePassword(self, MaxSize = 1):
        self.threads_launched = []
        for i in range(0,MaxSize):
            t = cracker.passGening( 1, i, i, current = "a" * i)
            t.start()
            self.threads_launched.append(t)




    # RUN UPD stuff
    def run(self):
        global MCAST_GRP
        global MCAST_PORT

        while self.role == None:
            try:
                payload, addr = self.sockUDP.recvfrom(1024)
            except socket.timeout:
                payload, addr = None, None

            if payload is not None:
                output = pickle.loads(payload)
                self.logger.debug("O: %s", output)
                print(f"O: ID {self.identification} {output}")
                print(output["IP"])
                print(type(tuple(output["IP"])))
                if output["command"] == "CON":
                    if self.identification > int(output["ID"]):
                        connectionMessage = {
                                "command":"OK",
                                "ID":self.identification,
                                "IP":(self.address,self.port)
                                }
                        print(output["IP"])
                        self.sockUDP.sendto(pickle.dumps(connectionMessage),tuple(output["IP"]))
                    else:
                        self.role = "Slave"

            if payload is None: # Socket Timeout
                connectionMessage = {
                        "command":"CON",
                        "ID":self.identification,
                        "IP":(self.address,self.port)
                        }
                self.sockUDP.sendto(pickle.dumps(connectionMessage),(MCAST_GRP,MCAST_PORT))

        while not self.done_UDP:
            payload, addr = self.socketUDP.recv()
            if payload:
                pass
            else: # Socket UDP Timeout Descobrir novo Coordenador
                pass

def main (secret, MSize, identification):
    s = Slave()
    s.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Basic HTTP Authentication Server Cracker')
    parser.add_argument('-l', dest='MaxSize', type=int, help="Max string length for passwords", default=1)
    parser.add_argument('-s', dest='secret',type=str, help="Secret To use", default=None)
    parser.add_argument('-i', dest='id',type=str, help="Id fo worker", default=1)
    #parser.add_arguments('-s', dest='secret',type=str, help="Secret To use", default=None)
    args = parser.parse_args()
    main(args.secret,args.MaxSize,args.id)
