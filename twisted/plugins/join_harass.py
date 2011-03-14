from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import random

class Harasser(object):
    implements(IPlugin, IIRCWatcher)

    onjoins = {
        "robovoyo":
          [ "beep boop beep beep boop",
            "/me hums a song in 7/4",
            "/me pantomimes a rock drummer.",
            "anyone want to get a sandwich as big as your head?", ],
        "tonytam":
          [ "folks, bouncing beta again.",
            "/me writes an undocumented API.",
            "/me breaks the Ivy config and doesn't tell anyone.",
            "/me goes and gets a mint from the bucket.", ],
        "esperluette":
          [ "/me defines some insanely obscure word without batting an eye",
            "/me writes a blog post about a dress.", ],
        "hobbeswalsh":
          [ "/me flexes his Python",
            "/me takes off his dorky Velcro bike shoes.",
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
