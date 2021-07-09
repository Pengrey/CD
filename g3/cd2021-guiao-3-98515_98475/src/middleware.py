"""Middleware to communicate with PubSub Message Broker."""
from collections.abc import Callable
from enum import Enum
import logging
from queue import LifoQueue, Empty
import queue
from src.broker import Serializer
from typing import Any
import socket
from .protocol import *

HOST = 'localhost'
port = 5000
clients= {}
queue = {}

class MiddlewareType(Enum):
    """Middleware Type."""

    CONSUMER = 1
    PRODUCER = 2



class Queue:
    """Representation of Queue interface for both Consumers and Producers."""
    
    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        """Create Queue."""
        self.topic = topic
        self._type = _type
        self.host = HOST
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connect()
        self.client.setblocking(True)     


    def connect(self):
        """Connect to chat server and setup stdin flags."""
        self.client.connect((self.host,self.port))
        logging.debug(f"Connected to {self.host} on port {self.port}")
        
    def receive(self,sock):
        """Receives message and prints it"""
        msg = CDProto.recv_msg(sock)
        return msg

    def push(self, value):
        """Sends data to broker. """ 
        CDProto.send_msg(self.client, CDProto.put( self.topic, value, self._format)) 

    def pull(self) -> (str, Any):
        """Waits for (topic, data) from broker."""
        # Should BLOCK the consumer!
        """CDProto.send_msg(self.client, CDProto.getData(self._format, self.topic))

        while True:
            events = self.sel.select()  
            for key, mask in events:    
                callback = key.data     
                msg = callback(key.fileobj)
                return (self.topic, msg.data)"""

        msg = self.receive(self.client)
        if msg:
            return self.topic, msg.data


    def list_topics(self, callback: Callable):
        """Lists all topics available in the broker."""
        CDProto.send_msg(self.client, CDProto.listReq(self._format))
        
        msg = self.receive(self.client)
        callback(msg)

        """while True:
            events = self.sel.select()  
            for key, mask in events:    
                callback = key.data     
                return callback(key.fileobj)"""


    def cancel(self):
        """Cancel subscription.""" 
        CDProto.send_msg(self.client, CDProto.unsub( self.topic, self.client, self._format))
    

class JSONQueue(Queue):
    """Queue implementation with JSON based serialization."""
    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type)
        self._format = Serializer.JSON.value
        if _type==MiddlewareType.CONSUMER:
            CDProto.send_msg(self.client, CDProto.sub(self.topic, self._format,))


class XMLQueue(Queue):
    """Queue implementation with XML based serialization."""
    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type)
        self._format = Serializer.XML.value
        if _type==MiddlewareType.CONSUMER:
            CDProto.send_msg(self.client, CDProto.sub(self.topic, self._format))


class PickleQueue(Queue):
    """Queue implementation with Pickle based serialization."""
    def __init__(self, topic, _type=MiddlewareType.CONSUMER):
        super().__init__(topic, _type)
        self._format = Serializer.PICKLE.value
        print(topic)
        if _type==MiddlewareType.CONSUMER:
            CDProto.send_msg(self.client, CDProto.sub(self.topic, self._format))


