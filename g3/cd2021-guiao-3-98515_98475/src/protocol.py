import json as j
import xml.etree.ElementTree as e
import pickle as p
import socket


class Message:
    """Message Type"""
    def __init__(self, command, form):
        self.command = command
        self.form = form


class GetDataMsg(Message):
    """Mensagem para obtenção do último valor no tópico "topic\""""
    def __init__(self, topic, form):
        super().__init__("get", form)   
        self.topic = topic

        self.message = {"command": self.command, "topic": self.topic}
        if self.form == 1:           
            root = e.Element("xml")
            e.SubElement(root, "command").text = str(self.command)
            e.SubElement(root, "topic").text = str(self.topic)
            self.message= e.tostring(root) 


class DataMsg(Message):
    """Mensagem com a resposta à mensagem "GetData\""""
    def __init__(self, data, form):
        super().__init__("data", form)   
        self.data = data

        self.message = {"command": self.command, "data": self.data}
        if self.form == 1:           
            root = e.Element("xml")
            e.SubElement(root, "command").text = str(self.command)
            e.SubElement(root, "data").text = str(self.data)
            self.message= e.tostring(root) 


class PutMsg(Message):
    """Mensagem para a publicação de um valor "val" no tópico "topic\""""
    def __init__(self, topic, val, form):
        super().__init__("put", form)   
        self.val = val
        self.topic = topic
        
        self.message = {"command": self.command, "topic": self.topic, "msg": self.val}    
        if self.form == 1:           
            root = e.Element("xml")
            e.SubElement(root, "command").text = str(self.command)
            e.SubElement(root, "topic").text = str(self.topic)
            e.SubElement(root, "msg").text = str(self.val)
            self.message= e.tostring(root) 


class SubMsg(Message):
    """Mensagem para adicionar um novo subscritor à lista de subscritores do tópico "topic\""""
    def __init__(self, topic, form):
        super().__init__("sub", form)   
        self.topic = topic

        self.message = {"command": self.command, "topic": self.topic}    
        if self.form == 1:    
            root = e.Element("xml")
            e.SubElement(root, "command").text = str(self.command)
            e.SubElement(root, "topic").text = str(self.topic)
            self.message= e.tostring(root)     


class UnSubMsg(Message):
    """Mensagem para remover um subscritor à lista de subscritores do tópico "topic\""""
    def __init__(self, topic, form):
        super().__init__("unsub", form)   
        self.topic = topic

        self.message = {"command": self.command, "topic": self.topic } 
        if self.form == 1:           
            root = e.Element("xml")
            e.SubElement(root, "command").text = str(self.command)
            e.SubElement(root, "topic").text = str(self.topic)
            self.message= e.tostring(root) 


class ListRequestMsg(Message):
    """Mensagem para pedido da lista de todos os tópicos"""
    def __init__(self, form):
        super().__init__("listReq", form) 

        self.message = {"command": self.command}  
        if self.form == 1:           
            root = e.Element("xml")
            e.SubElement(root, "command").text = str(self.command)
            self.message= e.tostring(root) 


class TopicsMsg(Message):
    """Mensagem com a resposta à mensagem "ListRequest\""""
    def __init__(self, topics, form):
        super().__init__("topics", form)   
        self.topics = topics

        self.message = {"command": self.command, "topics": self.topics}
        if self.form == 1:           
            root = e.Element("xml")
            e.SubElement(root, "command").text = str(self.command)
            e.SubElement(root, "topics").text = str(self.topics)
            self.message= e.tostring(root) 


class CDProto:
    """Computacao Distribuida Protocol."""

    @classmethod
    def getData(cls, topic, form) -> GetDataMsg:
        """Creates a GetDataMsg object."""
        return GetDataMsg(topic, form)

    @classmethod
    def data(cls, data, form) -> DataMsg:
        """Creates a DataMsg object."""
        return DataMsg(data, form)

    """PubMsg"""
    @classmethod
    def put(cls, topic, msg, form) -> PutMsg:
        """Creates a PubMsg object."""
        return PutMsg(topic, msg, form) 

    """SubMsg"""
    @classmethod
    def sub(cls, topic, form) -> SubMsg:
        """Creates a SubMsg object."""
        return SubMsg(topic,  form)

    """UnSubMsg"""
    @classmethod
    def unsub(cls, topic, form) -> UnSubMsg:
        """Creates a UnSubMsg object."""
        return UnSubMsg(topic,  form) 

    """ListReqMsg"""
    @classmethod
    def listReq(cls, form) -> ListRequestMsg:
        """Creates a ListRequestMsg object."""
        return ListRequestMsg(form)

    @classmethod
    def topics(cls, topics, form) -> TopicsMsg:
        """Creates a TopicsMsg object."""
        return TopicsMsg(topics, form)


    """Send Msg"""
    @classmethod
    def send_msg(cls, connection, msg):
        """Sends through a connection a Message object."""

        form = msg.form
        if form == 0:
            msg = j.dumps(msg.message).encode()
        elif form == 1: 
            msg = msg.message
        elif form == 2: 
            msg = p.dumps(msg.message)
        try:
            connection.send(form.to_bytes(1,byteorder='big') +len(msg).to_bytes(2,byteorder='big') + msg)
        except:
            pass


    @classmethod
    def recv_msg(cls, connection) -> Message:
        msgType = int.from_bytes(connection.recv(1), byteorder='big')
        length = int.from_bytes(connection.recv(2), byteorder='big')
        msg = b''
        read_bytes = 0
        while read_bytes < length:
            data = connection.recv(min(length - read_bytes,2048))
            if data == b'':
                raise RuntimeError("Couldn't read all data")
            msg += data
            read_bytes+= len(msg)
        if(msgType == 0):
            return cls.recv_msgJSON(msg)
        elif(msgType == 1):
            return cls.recv_msgXML(msg)      
        elif(msgType == 2):
            return cls.recv_msgPickle(msg)

    @classmethod
    def recv_msgJSON(cls, msg) :
        """Receives through a connection a Message object."""
        try:
            msg = j.loads(msg)
        except:
            pass
        if not msg == b'':
            command = msg["command"]
            if command == "get":    
                message = GetDataMsg(msg["topic"], 0)
            elif command == "data":
                message = DataMsg(msg["data"], 0)
            elif command == "put":
                message = PutMsg(msg["topic"], msg["msg"], 0)    
            elif command == "sub":
                message = SubMsg(msg["topic"],  0)
            elif command == "unsub":
                message = UnSubMsg(msg["topic"],  0)
            elif command == "listReq":
                message = ListRequestMsg(0)
            elif command == "topics":
                message = TopicsMsg(msg["topics"],  0)
            return message

    @classmethod
    def recv_msgXML(cls, msg) :
        """Receives through a connection a Message object."""
        try:
            root = e.fromstring(msg)       #check if this is right DONT FORGET LOVE <3
        except:
            pass
        if not root == b'':
            command= root[0].text
            if command == "get":    
                message = GetDataMsg(root[1].text, 1)
            elif command == "data":
                message = DataMsg(root[1].text, 1)
            elif command == "put":
                message = PutMsg(root[1].text, root[2].text, 1)    
            elif command == "sub":
                message = SubMsg(root[1].text,  1)
            elif command == "unsub":
                message = UnSubMsg(root[1].text,  1)
            elif command == "listReq":
                message = ListRequestMsg(1)
            elif command == "topics":
                message = TopicsMsg(root[1].text,  1)
            return message
    

    @classmethod
    def recv_msgPickle(cls, msg):
        """Receives through a connection a Message object."""
        if isinstance(msg, bytes):
            msg = p.loads(msg)
            if not msg == b'':
                command = msg["command"]   
                if command == "get":
                    message = GetDataMsg(msg["topic"], 2)
                elif command == "data":
                    message = DataMsg(msg["data"], 2)
                elif command == "put":
                    message = PutMsg(msg["topic"], msg["msg"], 2)    
                elif command == "sub":
                    message = SubMsg(msg["topic"],  2)
                elif command == "unsub":
                    message = UnSubMsg(msg["topic"],  2)
                elif command == "listReq":
                    message = ListRequestMsg(2)
                elif command == "topics":
                    message = TopicsMsg(msg["topics"],  2)
                return message      