import pickle
import socket
import struct

class Message:
    """Message Type"""
    def __init__(self, command):
        self.command = command


class CordMsg(Message):
    """Mensagem para informar o ID e o IP do coordenador"""
    def __init__(self,  id, ip):
        super().__init__("coordenador")   
        self.id= id  
        self.ip= ip
        self.message = {"command": self.command ,  "id" : self.id, "ip" : self.ip}

class DiscMsg(Message):
    """Mensagem para descobrir os id e ips dos slaves"""
    def __init__(self, id, ip):
        super().__init__("discover")
        self.id= id 
        self.ip = ip
        self.message = {"command": self.command , "id": self.id, "ip" : self.ip}


class ConnMsg(Message):
    """Mensagem para fazer uma eleição"""
    def __init__(self, id, ip):
        super().__init__("connect")
        self.ip= ip 
        self.id = id
        self.message = {"command": self.command , "id": self.id, "ip" : self.ip}

class WorkMsg(Message):
    """Mensagem do coordenador para o slave #ID que tente a palavra passe \"pwd\""""
    def __init__(self, id, init, pwd ):
        super().__init__("work")
        self.init= init 
        self.id = id
        self.pwd = pwd
        self.message = {"command": self.command , "id": self.id, "index": self.init, "token": self.pwd}

class DidItMsg(Message):
    """Mensagem para avisar que a palavra passe é a correta"""
    def __init__(self,  token):
        super().__init__("DID_ITo/")   
        self.token= token  
        self.message = {"command": self.command ,  "token" : self.token}


class NotDidItMsg(Message):
    """Mensagem para avisar que a palavra passe é a errada"""
    def __init__(self, id, index, token):
        super().__init__("NotDID_IT...")   
        self.index = index  
        self.token = token     
        self.id = id     
        self.message = {"command": self.command ,"index": self.index,  "token" : self.token, "id" : self.id}






class CDProto:
    """Computacao Distribuida Protocol."""
    
    @classmethod
    def cord(cls, id, ip) -> CordMsg:
        """Creates a CordMsg object."""
        return CordMsg(id,ip)

    @classmethod
    def disc(cls, id, ip) -> DiscMsg:
        """Creates a DiscMsg object."""
        return DiscMsg(id,ip)

    @classmethod
    def conn(cls, id, ip) -> ConnMsg:
        """Creates a ConnMsg object."""
        return ConnMsg(id,ip)

    @classmethod
    def work(cls, id, init, token) -> WorkMsg:
        """Creates a WorkMsg object."""
        return WorkMsg(id, init, token) 

    @classmethod
    def didIt(cls, token) -> DidItMsg:
        """Creates a DidItMsg object."""
        return DidItMsg( token) 

    @classmethod
    def notdidIt(cls, id, index , token) -> NotDidItMsg:
        """Creates a NotDidItMsg object."""
        return NotDidItMsg( id, index , token) 



    """Send multicast Msg"""
    @classmethod
    def send_multicast_msg(cls, connection, msg, destiny):
        """Sends through a connection a Message object."""
        try:
            connection.sendto(pickle.dumps(msg), destiny)
        except:
            pass

    """receive multicast Msg"""
    @classmethod
    def recv_multicast_msg(cls, connection) -> Message:
        try:                                                                                            # try to receive
            msg, addr = connection.recvfrom(1024)                                                 # get message 
        except socket.timeout:                                                                          # if timed out
            msg, addr = None, None 
        
        if msg is not None:   
            msg = pickle.loads(msg)   

        return  msg
