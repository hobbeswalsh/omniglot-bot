#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""
An IRC bot that will accept commands and log channels.
"""

# system imports
import time, sqlite3

from zope.interface import implements, Interface, Attribute
from twisted.internet import defer, threads, reactor, protocol


class IRCChannel(object):
    """An IRC channel"""

    def __init__(self, name, members=None):
        self.name = unicode(name)
        self.ops = {}
        self.voiced = {}
        self.periodics = {}
        self.disabledCommands = {}
        self._members = members or {}

    def getPeriodics(self):
        return self.periodics.values()

    def listPeriodics(self):
        return [ el.strip() for el in self.periodics.keys() ]

    @property
    def members(self):
        return self._members.keys()

    def addMember(self, user):
        if user in self.members:
            return
        self._members['user'] = int(time.time())

    def removeMember(self, user):
        if user in self.members:
            self._members.pop(user)

    def startedLurking(self, user):
        print "looking for user"
        print self.members
        if user not in self.members:
            return None
        return self._members['user']

    def unlurk(self, user):
        if user in self.members:
            self._members['user'] = int(time.time())

    def addPeriodic(self, command, args=None):
        cmd = " ".join([command, " ".join(args)])
        if cmd in self.periodics:
            return
        self.periodics[cmd] = (command, args)

    def removePeriodic(self, command, args=None):
        cmd = " ".join([command, " ".join(args)])
        if cmd in self.periodics:
            self.periodics.pop(cmd)

    def addVoiced(self, user):
        if user in self.voiced:
            return
        self.voiced['user'] = int(time.time())

    def addOp(self, user):
        if user in self.ops:
            return
        self.ops['user'] = int(time.time())
    
    def toggle(self, cmd):
        if self.disabledCommands.get(cmd) == 1:
            self.disabledCommands.pop(cmd)
            return "{0} re-enabled".format(cmd)
        else:
            self.disabledCommands[cmd] = 1
            return "{0} disabled".format(cmd)

    def isDisabled(self, cmd):
        now = int(time.time())
        return self.disabledCommands.get(cmd) == 1

    def getToggles(self):
        r  = "Disabled commands in {0}: ".format(self.name)
        r += ", ".join(self.disabledCommands.keys())
        return r

class IDBLogger(Interface):
    """Abstract database logger interface"""

    dbfile = Attribute("File we're logging to")
    schema = Attribute("Schema of all tables in the database")


    def log(table, *args):
        """Log whatever needs to be logged"""


class ChannelLogger(object):
    implements(IDBLogger)

    def __init__(self, dbfile, **kw):
        # XXX Ignore thread warnings from sqlite3.  Should be OK.
        # http://twistedmatrix.com/trac/ticket/3629
        kw.setdefault("check_same_thread", False)

        from twisted.enterprise.adbapi import ConnectionPool
        type = 'sqlite3'
        self.dbfile = dbfile
        self.dbconn = ConnectionPool(type, dbfile, **kw)
        self.table = 'channels'
        self.initialize_db()

    def initialize_db(self):
        return self.dbconn.runInteraction(self._initialize_db, self.table)

    @staticmethod
    def _initialize_db(tx, table):
        tx.execute('CREATE TABLE IF NOT EXISTS {0} ('
                   'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'timestamp INTEGER,'
                   'channel TEXT,'
                   'nick TEXT,'
                   'msg TEXT )'.format(table))

    def log(self, who, chan, msg):
        return self.dbconn.runInteraction(self._log, who, chan, msg, self.table)

    @staticmethod
    def _log(tx, who, chan, msg, table):
        now = int(time.time())
        stmt = 'INSERT INTO {0}(timestamp,nick,channel,msg) VALUES(?,?,?,?)'
        tx.execute(stmt.format(table), (now, who, chan, msg) )

if __name__ == '__main__':
    pass
