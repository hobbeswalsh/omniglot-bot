from zope.interface import implements
from twisted.plugin import IPlugin

from modules.interfaces import IMessageWatcher

class Logger(object):
    implements(IPlugin, IMessageWatcher)

    file = "/tmp/log.txt"
    f = open(file, "a")

    def gotMsg(self, msg):
        self.f.write("%s\n" % (msg,))
        return "logged %s" % (msg,)

e = Logger()
