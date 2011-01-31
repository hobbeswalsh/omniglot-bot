import re, urllib2
from zope.interface import implements, classProvides
from twisted.plugin import IPlugin
from modules.interfaces import *

class Tinifier(object):
    implements(IPlugin, IMessageWatcher, ICommandWatcher)
    #classProvides(IPlugin, IMessageWatcher)
    
    baseurl = "http://tinyurl.com/api-create.php?url="
    url_re  =  re.compile('(http(?:s)?://[\S]*)')

    def __init__(self):
        self.commands = { 'tiny': self.tiny }

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

    def gotMsg(self,channel,user,msg):
        tinied = []
        for found in self.url_re.findall(msg):
            if len(found) < 40:
                continue
            tinied.append(self._tiny(found))

        return ", ".join(tinied)

    def tiny(self, channel, user, args, irc=None):
        schma = 'http://'
        urls = [ schma + u for u in args if not u.startswith(schma) ]
        ret = [ self._tiny(url) for url in urls if self.url_re.match(url) ]
        return ", ".join(ret)

    def _tiny(self, url):
        ret = urllib2.urlopen(self.baseurl + url).read()
        if len(ret) > 40:
            return None
        return ret

    def help(self, cmd):
        if cmd == 'tiny':
            h = """Usage: tiny <url> :: I'll go ahead and tiny that url for ya."""
            return h


t = Tinifier()
