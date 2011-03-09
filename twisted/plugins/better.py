from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import json, urllib2

class Better(object):
    implements(IPlugin, ICommandWatcher)

    def __init__(self):
        self.commands = { 'better': self.getBetter }

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

    def getBetter(self, channel, user, args, irc=None):
        scores = []
        url = 'http://sucks-rocks.com/query?term='
        original_string = ' '.join(args)
        terms = original_string.split(' or ')
        if len(terms) <= 1:
            return None
        for term in terms:
            query = term.replace(" ", "+")
            u = url + query
            j = json.loads(urllib2.urlopen(u).read())
            sucks, rocks = j['sucks'], j['rocks']
            total = float(sucks + rocks)
            score = ( rocks / total ) * 10
            scores.append("{0:25}: {1:.1f}".format(term, score))
        return scores


    def help(self, cmd):
        if cmd == 'better':
            h = """Usage: ?better <term> or <term> ..."""
            return h

b = Better()
