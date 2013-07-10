# twisted imports
from zope.interface import Interface


class IMessageWatcher(Interface):

    """Watches all messages that come through the bot"""

    def gotMsg(channel, user, msg, irc=None):
        """We got a message"""


class ICommandWatcher(Interface):

    """Watches all commands that come through the bot"""

    def help():
        """Return a useful help message."""

    def provides():
        """Return a list of commands we provide"""

    def providesCommand(cmd):
        """Return True if we know how to provide the given command"""

    def gotCmd(channel, user, cmd, args, irc=None):
        """We got a command"""


class IActionWatcher(Interface):

    """Watches all actions that come through the bot"""

    def gotAction(channel, user, action, irc=None):
        """We got an action"""


class IIRCWatcher(Interface):

    """Watches all IRC events that come through the bot"""

    def gotPart(channel, user, irc=None):
        """Someone just left the channel"""

    def gotJoin(channel, user, irc=None):
        """Someone just joined the channel"""

    def gotNickChange(channel, oldnick, newnick, irc=None):
        """Someone just changed nicknames"""

    def joined(channel, irc=None):
        """Called when I join a channel"""
