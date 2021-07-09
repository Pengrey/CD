"""Message Broker"""

import enum
from typing import List
import socket
from enum import Enum
import selectors
from .protocol import *


class Node(object):
    def __init__(self, name):
        self.name = name        
        self.data = None
        self.subs = {}
        self.subNodes = []

def getNodeList(topic):
    """Get List of Node Names from path"""
    if(topic[0] == "/"):
        NodeList = topic.split("/")
        NodeList[0] = "/"
        if(topic == "/"): NodeList = ['/']
    else:
        NodeList = topic.split("/")
    return NodeList

def getNode(self, NodeList, create = False):
    """Get the Node and create it if permited"""
    
    NodeName = NodeList[0]

    # If in final Node
    if(len(NodeList) == 1):
        # Search if SubNode exists
        for subNode in self.subNodes:
            if(subNode.name == NodeName):
                return subNode

        # SubNode wasnt found
        if(create == True):
            # Create SubNode
            wantedNode = Node(NodeName)
            wantedNode.subs.update(self.subs)
            self.subNodes.append(wantedNode)
            return wantedNode
        else:
            return None
    
    # If not in final Node
    else:
        # Search if SubNode in SubNodes list
        for subNode in self.subNodes:
            if(subNode.name == NodeName):
                return getNode(subNode, NodeList[1:], create)
        
        # SubNode not in SubNodeList
        if(create == True):
            # Create new SubNode
            newSubNode = Node(NodeName)
            newSubNode.subs.update(self.subs)
            self.subNodes.append(newSubNode)
            return getNode(newSubNode, NodeList[1:], create)
        else:
            return None
    
def listTopics(self, path, list_of_topics):
    if(path == "" or path == "/"):
        path += self.name
    else:
        path += "/" + self.name

    if(self.data):
        list_of_topics.append(path)

    for subNode in self.subNodes:
        listTopics(subNode, path, list_of_topics)

def subNodes(self, address, _format):
    self.subs[address] = _format
    for subNode in self.subNodes:
        subNodes(subNode, address, _format)

def unsubNodes(self, address):
    self.subs.pop(address)
    for subNode in self.subNodes:
        unsubNodes(subNode, address)

class Serializer(enum.Enum):
    """Possible message serializers."""

    JSON = 0
    XML = 1
    PICKLE = 2


class Broker:
    """Implementation of a PubSub Message Broker."""

    def __init__(self):
        """Initialize broker."""
        self.canceled = False
        self._host = "localhost"
        self._port = 5000
        self.dirs = []
        self.sel = selectors.DefaultSelector()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self._host, self._port))
        self.server.listen()
        self.sel.register(self.server, selectors.EVENT_READ, self.accept)

    def accept(self, sock):
        conn, addr = sock.accept()
        self.sel.register(conn, selectors.EVENT_READ, self.read)
    
    def read(self, conn):
        msg = CDProto.recv_msg(conn)
        if msg:    
            comm = msg.command 
            if comm == "sub":
                toSend = self.get_topic(msg.topic)
                if toSend: 
                    CDProto.send_msg(conn, CDProto.data(toSend, msg.form))
                self.subscribe(msg.topic , conn, msg.form)
            elif comm == "put":
                self.put_topic(msg.topic, msg.val)
                subs = self.list_subscriptions(msg.topic)
                for sub in subs:
                    connection = sub[0]
                    form = sub[1]
                    CDProto.send_msg(connection, CDProto.data(msg.val,form))
            elif comm == "listReq":
                topics = self.list_topics()
                CDProto.send_msg(conn, CDProto.topics(topics, msg.form))
            elif comm == "unsub":
                self.unsubscribe(msg.topic, conn)
            elif comm == "get":
                data = self.get_topic(msg.topic)
                CDProto.send_msg(conn, CDProto.data(data, msg.form))
        
    def getRootNode(self, root):
        """Get Node correesponding to the root or create it if doesnt exist already"""
        # Find Node in dirs list
        for RootNode in self.dirs:
            if(RootNode.name == root): return RootNode

        # Create new dir with the new root
        NewRoot = Node(root)
        self.dirs.append(NewRoot)
        return NewRoot

    def list_topics(self) -> List[str]:
        """Returns a list of strings containing all topics."""
        list_of_topics = []
        for RootNode in self.dirs:
            listTopics(RootNode, "", list_of_topics)
        return list_of_topics

    def get_topic(self, topic):
        """Returns the currently stored value in topic."""   
        NodeList = getNodeList(topic)
        node = self.getRootNode(NodeList[0])
        if(len(NodeList) !=1):
            node = getNode(node, NodeList[1:])

        # Check if there is info on the topic
        if(node != None):
            return node.data
        else:
            return None
    
    def put_topic(self, topic, value):
        """Store in topic the value."""
        NodeList = getNodeList(topic)
        node = self.getRootNode(NodeList[0])
        if(len(NodeList) != 1):
            node = getNode(node, NodeList[1:], True)
        node.data = value

    def list_subscriptions(self, topic: str) -> List[socket.socket]:
        """Provide list of subscribers to a given topic."""
        NodeList = getNodeList(topic)
        node = self.getRootNode(NodeList[0])
        if(len(NodeList) != 1):
            node = getNode(node, NodeList[1:])
        return list(node.subs.items())

    def subscribe(self, topic: str, address: socket.socket, _format: Serializer = None):
        """Subscribe to topic by client in address."""
        NodeList = getNodeList(topic)
        node = self.getRootNode(NodeList[0])
        if(len(NodeList) != 1):
            node = getNode(node, NodeList[1:], True)
        subNodes(node, address, _format)

    def unsubscribe(self, topic, address):
        """Unsubscribe to topic by client in address."""
        NodeList = getNodeList(topic)
        node = self.getRootNode(NodeList[0])
        if(len(NodeList) != 1):
            node = getNode(node, NodeList[1:])
        unsubNodes(node, address)


    def run(self):  
        """Run until canceled."""
        try:
            while not self.canceled:
                events = self.sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj)
        except KeyboardInterrupt:
            self.server.close()      