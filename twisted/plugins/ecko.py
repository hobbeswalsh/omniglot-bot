from zope.interface import implements, classProvides
#from imessagewatcher import IMessageWatcher
from twisted.plugin import IPlugin

from modules.interfaces import *


class Echoer(object):
    implements(IPlugin, IMessageWatcher, IActionWatcher)

    def gotMsg(self, msg):
        return msg
    
    def gotAction(self, action):
        return "/me {0}".format(cmd)

e = Echoer()
