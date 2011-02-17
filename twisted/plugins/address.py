from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *

class Address(object):
    implements(IPlugin, ICommandWatcher)

    def __init__(self):
        self.commands = { 'address': self.getAddress }

    def provides(self):
        return self.commands.keys()

    def providesCommand(self, cmd):
        if cmd in self.commands:
            return True

    def gotCmd(self, channel, user, cmd, args, irc=None):
        if cmd not in self.commands:
            return
        c = self.commands[cmd]
        return c(channel, user, args, irc=None)

    def getAddress(self, channel, user, args, irc=None):
        address = list()
        address.append("195 E 4th Ave.")
        address.append("San Mateo, CA 94401")
        address.append("...jerk")
        return address

    def help(self, cmd):
        if cmd == 'address':
            h = """Wait, what's Wordnik's address again?"""
            return h

a = Address()
