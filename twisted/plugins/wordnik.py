from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import ConfigParser, os, re, time

class Wordnik(object):
    implements(IPlugin, IMessageWatcher, ICommandWatcher)

    configFile    = os.path.expanduser('~/.botrc')
    configSection = 'wordnik'
    configKey     = 'apikey'

    def __init__(self):
        self.commands = { 'lookup': self.lookup }
        self.c = ConfigParser.ConfigParser()
        self.c.read(self.configFile)
        self.apiKey = self.findKey()
        if self.apiKey == None:
            return None

    def findKey(self):
        if not self.c.has_section(self.configSection):
            print "Can't find section {0} in file {1}".format(self.configSection, self.configFile)
            return None
        if not self.c.has_option(self.configSection, self.configKey):
            print "Can't find key {0} in section {1} in file {2}".format(self.configKey, self.configSection, self.configFile)
            return None
        return self.c.get('wordnik', 'apikey')

    def gotMsg(self, channel, nick, msg, irc=None):
        return None

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

    def lookup(self, channel, user, args, irc=None):
        print self.apiKey
        print "looking up {0}".format(args)

    def help(self, cmd):
        if cmd == 'lookup':
            h = """Usage: lookup <word> :: I'll look up a word for you."""
            return h

wordnik = Wordnik()
