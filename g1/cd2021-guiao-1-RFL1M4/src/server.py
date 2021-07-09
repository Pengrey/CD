"""CD Chat server program."""
import logging
import selectors
import socket
from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename="server.log", level=logging.DEBUG) # logs for debug


class Server:
    """Chat Server process."""
    def __init__(self):
        """Server properties."""
        self.host = 'localhost'  # host IP address to be used on the server
        self.port = 9001 # TCP port to be used for data transfer
        self.sel = selectors.DefaultSelector() # instance selector object, DefaultSelector gets us the most efficient one at the moment
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creation of socket object, passed arguments make it that we use the IPv4 Internet address family and SOCK_STREAM means the socket type is TCP 
        self.server.bind((self.host,self.port)) # define host and port to be used on the server
        #self.server.setblocking(False) # Calls on the socket wont block it TODO maybe eliminate this
        self.server.listen()    #check number
        self.dic = {} #dictionary
        self.sel.register(self.server, selectors.EVENT_READ, self.accept) # registration to the monitor list

    def accept(self, sock):
        """Accepts connections and adds them to the server db if not already included"""
        conn, addr = self.server.accept()
        #self.server.setblocking(False) TODO maybe eliminate this
        logging.debug(f"Accepted: {conn}, {addr}")
        msg = CDProto.recv_msg(conn)
        name = msg.get() # name to later use on our db(database)
        logging.debug(f'Name: {name}')
        if conn not in self.dic: # adds to database if not in it already
            self.dic[conn] = [name, "None"]
        self.sel.register(conn, selectors.EVENT_READ, self.read) 
        logging.debug(f"Connected: [{conn},{self.dic[conn][0]}]")

    def read(self, conn):
        """Reads packages from socket and execs commands or sends message or terminates connection and eliminates online resence from db"""
        try:
            msg = CDProto.recv_msg(conn)
            logging.debug(f"Received: {msg}")
            if(msg.type() == "join"):
                tojoin = "None" if msg.get().rstrip() == "" else msg.get()
                if tojoin not in self.dic[conn]:
                    self.dic[conn].append(tojoin)
                else:
                    self.dic[conn].remove(tojoin)
                    self.dic[conn].append(tojoin)
                nchannels = len(self.dic[conn]) # get number of channels the client has
                logging.debug(f"Client {self.dic[conn][0]} joined {self.dic[conn][nchannels - 1]}")
            else:
                for user in self.dic:
                    for channel in self.dic[user]:
                        if(self.dic[conn][len(self.dic[conn]) - 1] == channel):
                            CDProto.send_msg(user,msg)
                            logging.debug(f"Sent {msg} to {self.dic[user][0]}")

        # If connection was terminated by client
        except CDProtoBadFormat:
            logging.debug(f"Exited: {self.dic[conn][0]}")
            self.sel.unregister(conn)
            self.dic.pop(conn)
            conn.close()

    def loop(self):
        """Loop indefinetely."""
        try:
            while True:
                events = self.sel.select() # blocks until one file descriptor is ready, returns list of ready objects
                for key, mask in events:   # for each file object ready returned 
                    callback = key.data    # get data from it 
                    callback(key.fileobj)  # get the file object from the data retrived
        
        except KeyboardInterrupt:   # closes server properly 
            self.server.close()
