from zope.interface import implements, classProvides
#from imessagewatcher import IMessageWatcher
from twisted.plugin import IPlugin

from modules.interfaces import *


class Echoer(object):
    implements(IPlugin, IMessageWatcher, ICommandWatcher)

    def gotMsg(self, msg):
        return msg
        #return None
    
    def gotCmd(self, cmd, args):
        return "okay whatever, I'll {0} {1}".format(cmd, args)

e = Echoer()
