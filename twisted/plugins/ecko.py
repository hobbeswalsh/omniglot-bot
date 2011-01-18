from zope.interface import implements, classProvides
#from imessagewatcher import IMessageWatcher
from twisted.plugin import IPlugin

from modules.interfaces import IMessageWatcher


class Echoer(object):
    implements(IPlugin, IMessageWatcher)

    def gotMsg(self, msg):
        return msg

e = Echoer()
