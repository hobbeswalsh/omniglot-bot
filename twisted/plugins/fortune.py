from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import json, random, time, urllib2

class Fortune(object):
    implements(IPlugin, ICommandWatcher)

    baseurl = "http://www.iheartquotes.com/api/v1/random?format=json"

    def __init__(self):
        self.commands = { 'fortune': self.getFortune }

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

    def getFortune(self, channel, user, args, irc=None):
        j = json.load(urllib2.urlopen(self.baseurl))
        q = j['quote']
        ret = q.replace('\n', ' ')
        ret = ret.replace('\r', ' ')
        ret = ret.replace('  ', ' ')
        return ret.__str__()

    def help(self, cmd):
        if cmd == 'beer':
            h = """Fetch a random beer! Yum!"""
            return h

f = Fortune()
