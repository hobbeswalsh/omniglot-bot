from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import pymongo, re, time

class MongoLogger(object):
    implements(IPlugin, IMessageWatcher, ICommandWatcher)

    def __init__(self):
        try:
            self.conn = pymongo.Connection()
        except:
            return None
        self.db = self.conn.irc
        self.collection = self.db.log
        self.commands = { 'said': self.searchLog }

    def gotMsg(self, channel, nick, msg, irc=None):
        now  = int(time.time())
        item = {"time":now,"channel":channel,"nick":nick,"msg":msg}
        oid = self.collection.save(item)
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

    def searchLog(self, channel, user, args, irc=None):
        found = list()
        if len(args) < 2:
            ## syntax is ?said <nick> <pattern>
            return None
        nick = args[0]
        pattern = re.compile(" ".join(args[1:]))
        query = { "msg": pattern, "nick": nick }
        cur = self.collection.find( query )
        if cur.count() == 0:
            return None
        for row in cur:
            nick    = row['nick']
            channel = row['channel']
            msg     = row['msg']
            found.append("{0} ({1}): {2}".format(nick,channel,msg))
        return found

    def help(self, cmd):
        if cmd == 'said':
            h = """Usage: said <nick> <regex> :: I will search the chat logs to see if <nick> said anything like <regex>."""
            return h

logger = MongoLogger()
