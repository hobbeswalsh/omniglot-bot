# twisted imports
from zope.interface import Interface

class IMessageWatcher(Interface):
    """Watches all messages that come through the bot"""

    def gotMsg(msg):
        """We got a message"""
