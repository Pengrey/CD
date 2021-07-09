"""CD Chat client program"""
import logging
import sys

from .protocol import CDProto, CDProtoBadFormat

logging.basicConfig(filename=f"{sys.argv[0]}.log", level=logging.DEBUG)


class Client:
    """Chat Client process."""

    def __init__(self, name: str = "Foo"):
        """Initializes chat client."""
        pass

    def connect(self):
        """Connect to chat server and setup stdin flags."""
        pass

    def loop(self):
        """Loop indefinetely."""
        pass
