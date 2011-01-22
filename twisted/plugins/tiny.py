import re, urllib2
from zope.interface import implements, classProvides
from twisted.plugin import IPlugin
from modules.interfaces import *

class Tinifier(object):
    implements(IPlugin, IMessageWatcher, ICommandWatcher)
    #classProvides(IPlugin, IMessageWatcher)
    
    baseurl = "http://tinyurl.com/api-create.php?url="
    url_re  =  re.compile('(http(?:s)?://[\S]*)')

    def gotMsg(self,channel,user,msg):
        tinied = []
        for found in self.url_re.findall(msg):
            if len(found) < 40:
                continue
            tinied.append(self._tiny(found))

        return ", ".join(tinied)

    def help(self, cmd):
        if cmd == 'tiny':
            h = """Usage: tiny <url> :: I'll go ahead and tiny that url for ya."""
            return h

    def provides(self):
        return [ 'tiny' ]

    def providesCommand(self, cmd):
        return cmd == 'tiny'

    def gotCmd(self, channel, user, cmd, args, irc=None):
        if cmd != 'tiny':
            return None
        ret = [ self._tiny(url) for url in args if self.url_re.match(url) ]
        return ", ".join(ret)

    def _tiny(self, url):
        return urllib2.urlopen(self.baseurl + url).read()


t = Tinifier()
