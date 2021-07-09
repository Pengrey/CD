import json as j
import socket
import struct

class Message:
    """Message Type"""
    def __init__(self, command):
        self.command = command


class AckMsg(Message):
    """Mensagem para enviar um token para o servidor"""
    def __init__(self, token, id):
        super().__init__("ACK")
        self.token= token 
        self.id = id
        self.message = {"comand": self.comand , "ID": self.ID, "token" : self.token}


class ConnectMsg(Message):
    """Mensagem para enviar um token para o servidor"""
    def __init__(self, id, host):
        super().__init__("conn")
        self.host= host 
        self.id = id
        self.message = {"comand": self.comand , "ID": self.id, "ip" : self.host}


class DidItMsg(Message):
    """Mensagem para avisar que o token é o correto """
    def __init__(self,  token):
        super().__init__("DID_IT\o/")   
        self.token= token  
        self.message = {"comand": self.comand ,  "token" : self.token}


class AckConnMsg(Message):
    """Mensagem para avisar que o token não é o correto """
    def __init__(self, host):
        super().__init__("ok")        
        self.host = host
        self.message = {"comand": self.comand , "host" : self.host}


class KeepAliveMsg(Message):
    """Mensagem para avisar que o token não é o correto """
    def __init__(self, id):
        super().__init__("keepAlive")        
        self.id = id
        self.message = {"comand": self.comand , "ID" : self.id}


class CoordenadorMsg(Message):
    """Mensagem para avisar que o token é o correto """
    def __init__(self,  id):
        super().__init__("coordenador")   
        self.id= id  
        self.message = {"comand": self.comand ,  "id" : self.id}


class EleicaoMsg(Message):
    """Mensagem para avisar que o token é o correto """
    def __init__(self,  id):
        super().__init__("eleicao")   
        self.ids = ids  
        self.message = {"comand": self.comand ,  "ids" : self.ids}


class PswdMsg(Message):
    """Mensagem para enviar um token para o servidor"""
    def __init__(self, host, token):
        super().__init__("pswd")           
        lines = [
            'GET / HTTP/1.1',
            'Host: {}'.format(self.host),
            'Authorization: Basic {}'.format(token),
            'Connection: keep-alive'
        ]
        self.message = '\r\n'.join(lines)+'\r\n\r\n'








class CDProto:
    """Computacao Distribuida Protocol."""

    @classmethod
    def pswd(cls, host, token) -> PswdMsg:
        """Creates a GetDataMsg object."""
        return PswdMsg(host, token) 
    
    @classmethod
    def didIt(cls, host, token) -> DidItMsg:
        """Creates a GetDataMsg object."""
        return DidItMsg(host, token) 
    
    @classmethod
    def keepAlive(cls, id) -> KeepAliveMsg:
        """Creates a GetDataMsg object."""
        return KeepAliveMsg(id) 

    @classmethod
    def ack(cls, token, id) -> AckMsg:
        """Creates a GetDataMsg object."""
        return AckMsg(token, id) 

    @classmethod
    def connect(cls, id, host) -> ConnectMsg:
        """Creates a GetDataMsg object."""
        return ConnectMsg(id, host)

    @classmethod
    def ackConn(cls, host) -> AckConnMsg:
        """Creates a GetDataMsg object."""
        return AckConnMsg(host)

    @classmethod
    def eleicao(cls, ids) -> EleicaoMsg:
        """Creates a GetDataMsg object."""
        return EleicaoMsg(ids)

    @classmethod
    def coordenador(cls, id) -> CoordenadorMsg:
        """Creates a GetDataMsg object."""
        return CoordenadorMsg(id)

    """Send Msg"""
    @classmethod
    def send_msg(cls, connection, msg):
        """Sends through a connection a Message object."""
        msg = j.dumps(msg.message).encode('utf-8')
        try:
            connection.send(len(msg).to_bytes(2,byteorder='big') + msg)
        except:
            pass


    @classmethod
    def recv_msg(cls, connection) -> Message:
        length = int.from_bytes(connection.recv(2), byteorder='big')
        msg = b''
        read_bytes = 0
        while read_bytes < length:
            data = connection.recv(min(length - read_bytes,2048))
            if data == b'':
                raise RuntimeError("Couldn't read all data")
            msg += data
            read_bytes+= len(msg)
            try:
                result = msg.decode('utf-8')
                result.split("\n")[-3]
            except:
                print("FOUND IT")
                return "FOUND IT"
            try:
                msg = j.loads(msg)
            except:
                pass
            if not msg == b'':
                command = msg["command"]
                if command == "DID_IT\o/":    
                    message = cls.didIt(msg["host"], msg["token"])
                elif command == "ACK":
                    message = cls.ack(msg["token"], mg["id"])
                elif command == "conn":
                    message = cls.connect(msg["id"], mg["ip"])
                elif command == "ok":
                    message = cls.ack(msg["host"])
                elif command == "keepAlive":
                    message = cls.keepAlive(msg["id"])
                elif command == "eleicao":
                    message = cls.eleicao(msg["ids"])
                elif command == "coordenador":
                    message = cls.coordenador(msg["id"])
                return message
