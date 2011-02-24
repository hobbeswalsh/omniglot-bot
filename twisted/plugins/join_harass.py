from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import random

class Harasser(object):
    implements(IPlugin, ICommandWatcher)

    onjoins = {
        "robovoyo":
          [ "beep boop beep beep boop",
            "/me hums a song in 7/4",
            "anyone want to get a sandwich as big as your head?", ],
        "hobbeswalsh":
          [ "/me flexes his Python",
            "the mail server broke again.", ],
      }

    def gotJoin(self, channel, user):
        if user in self.onjoins:
            return random.choice(self.onjoins.get(user))

    def gotPart(channel, user, irc=None):
        """not implemented"""
        pass

    def gotNickChange(channel, oldnick, newnick, irc=None):
        """not implemented"""
        pass

    def joined(channel, irc=None):
        """not implemented"""
        pass

h = Harasser()
