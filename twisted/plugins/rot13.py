from zope.interface import implements
from twisted.plugin import IPlugin

from modules.interfaces import IMessageWatcher

class Rot13er(object):
    implements(IPlugin, IMessageWatcher)

    lower = 'abcdefghijklmnopqrstuvwxyz'
    upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def gotMsg(self,msg):
        ret = ""
        for char in msg:
            if char in self.lower:
                ret += self.lower[((self.lower.find(char) + 13) % 26)]
            elif char in self.upper:
                ret += self.upper[((self.upper.find(char) + 13) % 26)]
            else:
                ret += char
        return ret

r = Rot13er()
