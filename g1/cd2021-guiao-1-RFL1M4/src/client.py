"""CD Chat client program"""
import logging
import sys
import socket
import fcntl
import os
import selectors
from .protocol import CDProto, CDProtoBadFormat

# sets sys.stdin to non-blocking
orig_fl = fcntl.fcntl(sys.stdin, fcntl.F_GETFL)
fcntl.fcntl(sys.stdin, fcntl.F_SETFL, orig_fl | os.O_NONBLOCK)

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        self.name = name
        self.host = 'localhost'  # host IP address to be used on the server
        self.port = 9001 # TCP port to be used for data transfer
        self.sel = selectors.DefaultSelector() # instance selector object, DefaultSelector gets us the most efficient one at the moment
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creation of socket object, passed arguments make it that we use the IPv4 Internet address family and SOCK_STREAM means the socket type is TCP 

    def getInput(self,stdin):
        """Gets input from stdin and either excs command or sends message"""
        input = stdin.read().rstrip("\n").split()   # gets input and strips next line at the end and makes a list with the input
        if input[0] == 'exit':
            self.client.close()
            exit()
        elif input[0] == '/join':
            join = "None" if len(input) == 1 else input[1]
            msg = CDProto.join(join)
            CDProto.send_msg(self.client,msg)
            logging.debug(f"Joined: {join}")
        else:
            if input:
                input = " ".join(input) # converts string list into string
                CDProto.send_msg(self.client,CDProto.message(input))
                logging.debug(f"Sent: {CDProto.message(input)}")

    def receive(self,sock):
        """Receives message and prints it"""
        msg = CDProto.recv_msg(sock)
        logging.debug(f"Received: {str(msg)}")
        if msg:
            sys.stdout.write(f"\b<{str(msg.get())}\n")
            sys.stdout.flush()

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.client.connect((self.host,self.port))
        logging.debug(f"Connected to {self.host} on port {self.port}")
        CDProto.send_msg(self.client, CDProto.register(self.name)) # registers client on the server
        self.sel.register(sys.stdin, selectors.EVENT_READ, self.getInput) # adds stdin into watch list
        self.sel.register(self.client, selectors.EVENT_READ, self.receive) # adds client to handle receiving messages
        self.client.setblocking(False)

    def loop(self):
        """Loop indefinetely."""
        while True:
            events = self.sel.select()  # blocks until one file descriptor is ready, returns list of ready objects
            for key, mask in events:    # for each file object ready returned 
                callback = key.data     # get data from it 
                callback(key.fileobj)   # get the file object from the data retrived
            sys.stdout.write(">")       # adds a nice ">" on the console
            sys.stdout.flush()