from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import ConfigParser, json, os, random, re, time, urllib2

class Wordnik(object):
    implements(IPlugin, IMessageWatcher, ICommandWatcher)

    configFile    = os.path.expanduser('~/.botrc')
    configSection = 'wordnik'
    configKey     = 'apikey'

    url   = "http://api.wordnik.com/api"
    key   = "?api_key=9554cd51b3ae7593536040047c20e2ac3ce71b2fd01cf1a27"
    limit = "&limit=100"

    def __init__(self):
        self.commands = {
                          'lookup': self.lookup,
                          'bigram': self.bigram
                        }
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
        if random.randint(0,1000) > 990:
            return
        try:
            word = random.choice(msg.split())
        except:
            return None
        return self.bigram(channel, nick, [word])

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
        found = list()
        url = self.url + "/word.json"
        for word in args:
            wordurl = url + "/{0}/definitions" + self.key
            r = self.fetch(wordurl.format(word))
            if r is None:
                continue
            found.append(json.loads(r))
        ret = list()
        for defs in found:
            try:
                bestdef = defs[0]
                ret.append(bestdef['text'].__str__())
            except:
                continue
        return ret

    def bigram(self, channel, user, args, irc=None):
        ret = list()
        url = self.url + "/word.json"
        for word in args:
            wordurl = url + "/{0}/phrases" + self.key + self.limit
            r = self.fetch(wordurl.format(word))
            if r is None:
                continue
            found = json.loads(r)
            if len(found) == 0:
                continue
            choice = random.choice(found)
            gram1 = choice['gram1'].__str__()
            gram2 = choice['gram2'].__str__()
            ret.append(gram1 + " " + gram2)
        return ret

    def fetch(self, url):
        try:
            return urllib2.urlopen(url).read()
        except:
            return None


    def help(self, cmd):
        if cmd == 'lookup':
            h = """Usage: lookup <word> :: I'll look up a word for you."""
            return h

wordnik = Wordnik()
