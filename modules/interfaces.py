# twisted imports
from zope.interface import Interface

class IMessageWatcher(Interface):
    """Watches all messages that come through the bot"""

    def gotMsg(msg):
        """We got a message"""

class ICommandWatcher(Interface):
    """Watches all commands that come through the bot"""

    def gotCmd(cmd):
        """We got a command"""

class IActionWatcher(Interface):
    """Watches all actions that come through the bot"""

    def gotAction(action):
        """We got an action"""

class IIRCWatcher(Interface):
    """Watches all IRC events that come through the bot"""

    def gotPart(user):
        """Someone just left the channel"""

    def gotJoin(user):
        """Someone just joined the channel"""

    def gotNickChange(oldnick, newnick):
        """Someone just changed nicknames"""


