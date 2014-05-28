#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
An IRC bot that will accept commands and log channels.
"""

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import defer, threads, reactor, protocol
from twisted.internet.task import LoopingCall
from twisted.python import log, rebuild
from xml.etree.ElementTree import fromstring as read_xml


# system imports
import datetime, time, sys, os, getpass, re, sqlite3, urllib2

# custom imports
import commands, helper

class DNSBot(object):
    """This is the "brain" of the IRC bot."""

    def __init__(self):
        self.name           = "nibor"
        self.username       = "nibor"
        self.masters        = ['~rwalsh@dev1.wordnik.com']
        self.configfile     = "/tmp/{0}.txt".format(self.name)
        self._channels      = {}
        self._quietChannels = []
        self.loopers        = []
        self.channel_log    = os.getcwd() + '/log/logs.db'
        self.logger         = helper.ChannelLogger(self.channel_log)
        self.loggy          = log
        self.loggy.msg('set logger')

        ## How do we get the bot's attention? Start a line with one
        ## of the following.
        self.cmd1           = '?'
        self.cmd2           = '{0}:'.format(self.name)
        self.url_re         =  re.compile('(?P<url>http(?:s)?://[\S]*)')


    def connectionMade(self, irc, secret=None):
        self._irc = irc
        self.readState()
        try:
            helper = rebuild.rebuild(helper, doLog=0)
        except:
            pass

        self.periodic_commands = LoopingCall(self.do_periodics)
        self.periodic_commands.start(1800)
        self.loopers.append(self.periodic_commands)

    def connectionLost(self):
        self._irc = None

    def getPass(self):
        return self.secret

    def addChannel(self, name):
        if name in self.channels:
            return
        self._channels[name] = helper.IRCChannel(name)
    
    def getChannel(self, name):
        return self._channels.get(name)

    def startTalking(self, name):
        if name in self.quietChannels:
            self._quietChannels.remove(name)

    def stopTalking(self, name):
        if name in self.quietChannels:
            return
        self._quietChannels.append(name)

    def joined(self, channel):
        self.addChannel(channel)
        self.writeState()

    def gotNames(self, channel, names):
        if channel not in self._channels:
            ## something went wrong, but we don't really care
            return

        ## add all names in the channel to our (stupid) data structure.
        for name in names:
            isOp = (name[0] == "@")
            isVoiced = (name[0] == "+")
            if isOp or isVoiced:
                name = name[1:]

            chan = self.getChannel(channel)
            if chan is None:
                return

            chan.addMember(name)
            if isOp:
                chan.addOp(name)
            if isVoiced:
                chan.addVoiced(name)

    def leaveChannel(self, channel):
        if channel in self.channels:
            self._irc.msg(channel, "*sniff*")
            self._irc.part(channel)
            leftchannel = self._channels.pop(channel)
            self.writeState()
        else:
            msg = "Yeah.... I'll get right on that."
            self.say(msg, channel, channel)

    def readState(self):
        try:
           print "oprning config {0}".format(self.configfile)
           f_chans = open(self.configfile)
        except IOError:
            return

        allChans = [chan.strip() for chan in f_chans.readlines()]
        for channel in allChans:
            self._irc.join(channel)
            self.addChannel(channel)

    def writeState(self):
        f_chans = open(self.configfile, "w")
        [f_chans.write(channel + "\n") for channel in self.channels]
        f_chans.close()

    def do_periodics(self):
        self.loggy.msg("periodics!")
        for channel in self.channels:
            ## update list of names
            self._irc.names(channel)

            ## I don't need to perform any periodics in quiet channels
            if channel in self.quietChannels:
                continue

            chan = self.getChannel(channel)
            periodics = chan.getPeriodics()
            for item in periodics:
                cmd = item[0]
                args = item[1]
                self.gotCommand(cmd, args, channel, channel)
            self.stopTalking(channel)

        self.writeState()

    @property
    def channels(self):
        return self._channels.keys()

    @property
    def quietChannels(self):
        return self._quietChannels

    def emit_slowly(self, m, replyTo, lines):
        for line in lines:
            m(replyTo, line)
            time.sleep(1)

    def emit(self, m, replyTo, lines):
        [ m(replyTo, line) for line in lines]

    def say(self, msg, replyTo, user):
        if not msg:
            return

        if msg.startswith('ACT'):
            msg = msg.replace('ACT', '')
            m = self._irc.describe
        else:
            m = self._irc.msg

        lines = msg.split("\n")
        if len(lines) > 3:
            replyTo = user
        if len(lines) > 10:
            return threads.deferToThread(self.emit_slowly, m, replyTo, lines)

        return threads.deferToThread(self.emit, m, replyTo, lines)

    def errorCmd(self, error, cmd, replyTo):
        msg = "{0} failed at {1}".format(cmd, datetime.datetime.now())
        self.gotCommand("feature", [msg], self.name, self.name)

    def gotMsg(self, user, replyTo, msg):
        if replyTo in self.channels:
            chan = self.getChannel(replyTo)
            chan.unlurk(user)
        #self.logger.log(user, replyTo, msg)
        self.startTalking(replyTo)
        self.parseMsg(user, replyTo, msg)

    def gotAction(self, user, replyTo, act):
        pass

    def parseMsg(self, user, replyTo, msg):
        if msg.startswith(self.cmd1) or msg.startswith(self.cmd2):
            cmd = msg.replace(self.cmd1,'',1).replace(self.cmd2,'',1).strip()
            command_line = cmd.split(" ")
            cmd = command_line[0]
            args = command_line[1:]
            self.gotCommand(cmd, args, replyTo, user)
        if self.url_re.search(msg):
            url = self.url_re.search(msg).groupdict()['url']
            if len(url) > 40:   
                cmd = 'tiny'
                args = [ url ]

                ## spacial handling for special urls
                if ( 'XXXplaceholderXXX' in url 
                  and 'id=' in url
                  and 'show_bug.cgi' in url):
                    cmd = 'bug'
                    bug_re = re.compile('.*id=([0-9]+)')
                    m = bug_re.match(url)
                    if m is None:
                        cmd = 'tiny'
                        args = [ url ]
                    else:
                        args = [ m.groups()[0] ]
                if 'XXXplaceholderXXX' in url:
                    cmd = 'siebel'
                    args = [ url.split('=')[-1] ]
                if 'XXXplaceholderXXX' in url:
                    cm_re = re.compile('.*cmr_id/([0-9]+)|.*cmr_id=([0-9]+)')
                    m = cm_re.match(url)
                    if m is None:
                        cmd = 'tiny'
                        args = [ url ]
                    else:
                        for match in m.groups():
                            if match is None:
                                continue
                            cmd = 'cm'
                            args = [ match ]

                self.gotCommand(cmd, args, replyTo, user)

    def gotCommand(self, cmd, args, replyTo, user):

        ##########################################################
        ## maybe I'll break out these special commands at some point
        if cmd == "leave":
            self.leaveChannel(replyTo)
            return

        if cmd == "help" or cmd == "said":
            replyTo = user


        if cmd == "reload":
            self.say("reloading", replyTo, replyTo)
            for looper in self.loopers:
                looper.stop()
                self.loopers.remove(looper)
            self._irc.reload()
            return

        ### stupid aliasing.... <grumble>
        if cmd == "countdown":
            cmd = "timer"

        if cmd == "timer":
            wait = args[0]
            try:
                wait = int(wait)
            except ValueError:
                return
            c = args[1]
            args = args[2:]
            reactor.callLater(wait, self.gotCommand, c, args, replyTo, user)
            return


        if cmd == "add_periodic":
            if replyTo not in self.channels:
                return
            print "adding periodic in {0}".format(replyTo)
            channel = self.getChannel(replyTo)
            cmd = args[0]
            args = args[1:]
            channel.addPeriodic(cmd, args)
            return

        if cmd == "remove_periodic":
            if replyTo not in self.channels:
                return
            print "removing periodic in {0}".format(replyTo)
            channel = self.getChannel(replyTo)
            cmd = args[0]
            args = args[1:]
            channel.removePeriodic(cmd, args)
            return

        if cmd == "periodics":
            if replyTo not in self.channels:
                return
            channel = self.getChannel(replyTo)
            self.say(", ".join(channel.listPeriodics()), replyTo, replyTo)


        if cmd == "toggle":
            if replyTo not in self.channels:
                return
            channel = self.getChannel(replyTo)
            toToggle = args[0]
            c = commands.Commander()
            if c.getCommand(toToggle) is None:
                return
            self.say(channel.toggle(toToggle), replyTo, replyTo)

        if cmd == "toggles":
            if replyTo not in self.channels:
                return
            channel = self.getChannel(replyTo)
            self.say(channel.getToggles(), replyTo, replyTo)
        if cmd == "lurk":
            return
            who = args[0]
            if replyTo not in self.channels:
                return
            channel = self.getChannel(replyTo)
            startedLurking = channel.startedLurking(who)
            if startedLurking is None:
                self.say("{0} isn't in the channel, dolt.".format(who), replyTo, replyTo)
                return
            lurkTime = int( (int(time.time()) - startedLurking ) / 60 )
            self.say("{0} has been lurking for {1} minutes.".format(who, lurkTime), replyTo, replyTo)

        ##
        ##########################################################

        if replyTo in self.channels:
             channel = self.getChannel(replyTo)
             if channel.isDisabled(cmd):
                 return


        ## try to rebuild the Commander in case anything has changed...
        try:
            m = rebuild.rebuild(commands, doLog=0)
            c = m.Commander()
        except:
            c = commands.Commander()

        c.setChannelLog(self.channel_log)
        ## Here there be drago... er, Deferreds.
        print "Running {0} for {1}".format(cmd, replyTo)
        d = threads.deferToThread(c.callCommand, self, cmd, args)
        d.addCallback(self.say, replyTo, user)
        d.addErrback(self.errorCmd, cmd, replyTo)
        return

    def printError(self, something, cmd):
        print "timed out running {0}".format(cmd)
