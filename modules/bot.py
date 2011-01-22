#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
An IRC bot that must be instantiated with a brain (see modules/brain.py)
"""

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, threads, defer
from twisted.internet.task import LoopingCall
from twisted.python import log, rebuild

from twisted.plugin import IPlugin, getPlugins
import interfaces

## Prevent endless caching of plugin behavior
import sys
sys.dont_write_bytecode = True

class Client(irc.IRCClient):
    """ A simple wrapper around irc.IRCClient
    """

    def connectionMade(self):
        """Called when a connection is made"""
        self.setNick(self.factory.getNick())
        self.commandChar = self.factory.getCommandChar()
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        """Called when a connection is lost"""

    ## callbacks for events
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        for channel in self.factory.getChannels():
            self.join(channel)
        self.setNick(self.factory.getNick())
        self.startLoopers()

    def joined(self, channel, *args):
        """This will get called when the bot joins the channel."""
        self.factory.addChannel( channel )

    def names(self, channel):
        """Send a NAMES request to a channel"""
        if not channel:
            return
        msg = "NAMES {0}".format(channel)
        self.sendLine(msg)

    def irc_RPL_NAMREPLY(self, prefix, reply):
        """This gets called when we get a reply to NAMES"""

    #def userJoined(self, user, channel):
    #    """Called when a user joins a channel"""
    #    self.names(channel)

    #def userLeft(self, user, channel):
    #    """Called when a user leaves a channel"""
    #    self.names(channel)

    #def userRenamed(self, oldname, newname):
    #    """Called when a user changes nick???"""
    #    self.names(channel)

    def left(self, channel):
        """This will get called when the bot leaves a channel."""

    def privmsg(self, user, replyTo, msg):
        """This will get called when the bot receives a message."""
        mask = None
        if user.count('!') > 0:
            (user, mask) = user.split('!', 1)

        if replyTo == self.nickname:
            replyTo = user

        if self.isCommand(msg):
            return self.processCmd(msg, replyTo, user)
        else:
            return self.processMsg(msg, replyTo, user)

    def processCmd(self, msg, replyTo, user):
        cmd, args = self.parseCmd(msg)
        if cmd is None:
            return

        if cmd == 'help':
            return self.sendHelp(user, args)

        self.gatherPlugins()

        for plgn in self.cmdPlugins:
            d = threads.deferToThread(plgn.gotCmd, replyTo, user, cmd, args)
            d.addCallback(self.emit, replyTo, user)

    def processMsg(self, msg, replyTo, user):
        self.gatherPlugins()

        for plgn in self.msgPlugins:
            d = threads.deferToThread(plgn.gotMsg, replyTo, user, msg)
            d.addCallback(self.emit, replyTo, user)

    def sendHelp(self, user, args):
        if len(args) == 0:
            return self.sendGenericHelp(user)

        self.gatherPlugins()
        for cmd in args:
            for plgn in self.cmdPlugins:
                if plgn.providesCommand(cmd):
                    d = threads.deferToThread(plgn.help, cmd)
                    d.addCallback(self.emit, user)

    def sendGenericHelp(self, user):
        h = """Here are the commands I know about:"""
        knownCommands = list()

        self.gatherPlugins()
        for plgn in self.cmdPlugins:
            provides = plgn.provides()
            if type(provides) != type(list()):
                continue
            knownCommands.extend(provides)
        h += ", ".join(knownCommands) + ".\n"
        h += "type help <command> to get help on individial commands.\n"
        self.emit(h, user)

    def userjoined(self, user, channel, data):
        """This will get called when a user joins the channel"""
        print "{0} just joined!".format(user)

    def action(self, user, replyTo, act):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]

        if replyTo == self.nickname:
            replyTo = user

        self.gatherPlugins()

        for plgn in self.actPlugins:
            d = threads.deferToThread(plgn.gotAction, replyTo, user, act, irc=self)
            d.addCallback(self.emit, replyTo, user)

    def emit(self, msg, dest, user=None):
        if type(msg) == type(list()):
            if len(msg) > 2:
                dest = user
            return [ self.emitString(line, dest) for line in msg ]
        else:
            return self.emitString(msg, dest)

    def emitString(self, msg, dest):
        if msg is None:
            return
        if msg.startswith('/me '):
            msg = msg.replace('/me ', '')
            self.describe(dest, msg)
        else:
            self.msg(dest, msg)

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]

    def irc_INVITE(self, mask, where):
        """Called when someone invites me to a channel"""
        (nick, channel) = where
        self.join(channel)
        self.joined(channel)
        self.msg(channel, "Thanks, {0}!".format(mask.split('!')[0]))

    ## maintenance callback
    def irc_PING(self, prefix, params):
        """Called when we get PINGed. Maybe."""
        ### ...aand, the pong (forgot this earlier)
        self.sendLine("PONG %s" % params[-1])

    def startLoopers(self):
        """This is all the loopers we start
        """
        self.periodic_commands = LoopingCall(self.periodics)
        self.periodic_commands.start(1800)

    def periodics(self):
        """Nothing to see here, move along...
        """
        pass

    def gatherPlugins(self, type=None):
        self.msgPlugins = getPlugins(interfaces.IMessageWatcher)
        self.cmdPlugins = getPlugins(interfaces.ICommandWatcher)
        self.actPlugins = getPlugins(interfaces.IActionWatcher)

    def isCommand(self, msg):
        if msg.startswith(self.commandChar):
            return True
        elif msg.startswith(self.nickname + ":"):
            return True
        else:
            return False

    def parseCmd(self, msg):
        
        if msg.startswith(self.nickname + ":"):
            pattern = "{0}:".format(self.nickname)
        elif msg.startswith(self.commandChar):
            pattern = self.commandChar

        m = msg.replace(pattern, "")
        c = m.strip().split()
        cmd = c[0]
        if len(c) > 1:
            args = c[1:]
        else:
            args = []
        if cmd == "reload":
           self.factory.reload()
           return None, None
        return (cmd, args)


class Factory(protocol.ClientFactory):
    """
    A factory for IRC Clients.
    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, name, protocol):
        self.protocol = protocol
        self.nickname = name
        self.name = name
        self.protocol.nickname = name
        self.commandChar = '?'
        self.channels = {}

    def getNick(self):
        return self.nickname

    def reload(self):
        reactor.callLater(5, self.service.startService)
        self.service.stopService()
        #self.service.connector = Factory()

    def getCommandChar(self):
        return self.commandChar

    def getChannels(self):
        return self.channels.keys()

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        pass
        #connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

    def addChannel(self, channel):
        self.channels[channel] = 1
