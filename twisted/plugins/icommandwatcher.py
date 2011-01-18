# twisted imports
from zope.interface import Interface, implements

class ICommandWatcher(Interface):
    """Watches all messages that come through the bot"""

    def gotCmd(msg):
        """We got a command"""
