#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
An IRC bot that must be instantiated with a brain (see modules/brain.py)
"""


# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, threads
from twisted.python import log, rebuild

from twisted.plugin import getPlugins
from interfaces import IMessageWatcher

class Client(irc.IRCClient):
    """
    A simple wrapper around irc.IRCClient that will try to stay connected to 
    the IRC server and 
    """
    
    def __init__(self):
        pass
    
    def connectionMade(self):
        """Called when a connection is made"""
        irc.IRCClient.connectionMade(self)
        # hand a copy of self to self.brain (so the bot can talk to IRC)

    def connectionLost(self, reason):
        """Called when a connection is lost"""
        irc.IRCClient.connectionLost(self, reason)
        # tell the brain it's disconnected?

    ## callbacks for events
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.setNick(self.factory.getNick())

    def joined(self, channel, *args):
        """This will get called when the bot joins the channel."""

    def names(self, channel):
        """Send a NAMES request to a channel"""
        if not channel:
            return
        msg = "NAMES {0}".format(channel)
        self.sendLine(msg)

    def irc_RPL_NAMREPLY(self, prefix, reply):
        """This gets called when we get a reply to NAMES"""
        channel = reply[2]
        names = reply[3].split()

    def userJoined(self, user, channel):
        """Called when a user joins a channel"""
        self.names(channel)

    def userLeft(self, user, channel):
        """Called when a user leaves a channel"""
        self.names(channel)

    # XXX This does not appear to get called on nick change
    #def userRenamed(self, oldname, newname):
    #    """Called when a user changes nick???"""
    #    self.names(channel)

    def left(self, channel):
        """This will get called when the bot leaves a channel."""

    def reload(self):
        pass

    def privmsg(self, user, replyTo, msg):
        """This will get called when the bot receives a message."""
        mask = None
        if user.count('!') > 0:
            (user, mask) = user.split('!', 1)

        if replyTo == self.nickname:
            replyTo = user

        cmds = getPlugins(IMessageWatcher)
        for cmd in cmds:
            d = threads.deferToThread(cmd.gotMsg, msg)
            d.addCallback(self.emit, replyTo)

    def emit(self, msg, dest):
        self.msg(dest, msg)


    def action(self, user, replyTo, act):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]

        if replyTo == self.nickname:
            replyTo = user

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]

    def irc_INVITE(self, mask, where):
        print "just got an invite"
        """Called when someone invites me to a channel"""
        (nick, channel) = where
        self.join(channel)
        self.msg(channel, "Thanks, {0}!".format(mask.split('!')[0]))

    ## maintenance callback
    def irc_PING(self, prefix, params):
        """Called when we get PINGed. Maybe."""
        ### ...aand, the pong (forgot this earlier)
        self.sendLine("PONG %s" % params[-1])

class Factory(protocol.ClientFactory):
    """
    A factory for IRC Clients.
    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self):
        self.protocol = Client
        self.nick = 'defaultBot'

    def getNick(self):
        return self.nick

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

def usage(exitcode):
    print "Usage: {0} [server]".format(sys.argv[0])
    sys.exit(exitcode)
