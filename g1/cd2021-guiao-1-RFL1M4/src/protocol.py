"""Protocol for chat server - Computação Distribuida Assignment 1."""
import json
from datetime import datetime
from socket import socket


class Message:
    """Message Type."""
    def __init__(self, command):
        self._command = command
    
    def __str__(self):
        return f"Command: {self._command}"
    
class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self, command, channel):
        super().__init__(command)
        self._channel = channel

    def __str__(self):
        return f"{{\"command\": \"{self._command}\", \"channel\": \"{self._channel}\"}}"
    
    def get(self):
        return self._channel
    
    def type(self):
        return self._command

class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, command, user):
        super().__init__(command)
        self._user = user

    def __str__(self):
        return f"{{\"command\": \"{self._command}\", \"user\": \"{self._user}\"}}"
    
    def get(self):
        return self._user
    
    def type(self):
        return self._command
    
class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self, command, msg, channel):
        super().__init__(command)
        self._msg = msg
        self._channel = channel
        self._ts = int(datetime.now().timestamp())

    def __str__(self):
        if(self._channel != None):
            return f"{{\"command\": \"{self._command}\", \"message\": \"{self._msg}\", \"channel\": \"{self._channel}\", \"ts\": {self._ts}}}"
        else:
            return f"{{\"command\": \"{self._command}\", \"message\": \"{self._msg}\", \"ts\": {self._ts}}}"
    
    def get(self):
        return self._msg
    
    def type(self):
        return self._command

class CDProto:
    """Computação Distribuida Protocol."""

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        register = str(RegisterMessage("register",username))
        return register

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        join = str(JoinMessage("join",channel))
        return join

    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        msg = str(TextMessage("message", message, channel))
        return msg

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        msg = str(msg).encode("utf-8")
        connection.sendall(len(msg).to_bytes(2,"big"))
        total_sent = 0
        while total_sent < len(msg):
            sent = connection.send(msg[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        size = int.from_bytes(connection.recv(2), byteorder = 'big') # get size of the mensage to be later received
        chunks = [] # array to insert received packages
        bytes_read = 0 # bytes read until now
        while bytes_read < size: # receive packages until received all
            chunk = connection.recv(min(size - bytes_read, 2048))
            if chunk == b'':    # if we receive nothing then the connection was broken
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_read = bytes_read + len(chunk)
        msg = (b''.join(chunks)).decode('utf-8') # decodes message
        try:
            msg = json.loads(msg)
        except:
            raise CDProtoBadFormat
        key = msg.get('command')
        if key == 'join':
            return JoinMessage(key, msg.get('channel'))
        elif key == 'register':
            return RegisterMessage(key, msg.get('user'))
        elif key == 'message':
            return TextMessage(key, msg.get('message'),msg.get('ts'))
        
class CDProtoBadFormat(Exception):
    """Exception when source message is not CDProto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")
