from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import os, random

class Disser(object):
    implements(IPlugin, ICommandWatcher)

    disses = [
      "submits a bug report about {0}.",
      "has a word with {0}'s manager.",
      "tells a raunchy yo'-momma joke about {0}.",
      "tweets something negative about {0}.",
      "spits chai on {0}'s laptop.",
      "fakes a high-five with {0} but pulls back at the last minute.",
      "says something about {0} that merits an 'oh snap!'",
      "gives {0} the cold shoulder.",
      "gives {0} the hairy eyeball.",
      "mumbles under his breath about {0}.",
      "submits a post about {0} to failblog.org.",
      "signs a petition barring {0} from public spaces.",
      "motions to have {0} deported to Cydonia.",
      "takes away {0}'s Legos.",
      "posts on urbandictionary.com about {0}.",
      "writes a 'prettiest princess' e-mail from {0}\'s account.",
      "messes with {0}'s chair.",
      "puts tape under {0}'s mouse.",
      "steals {0}'s stapler.",
      "repeatedly sends lewd IMs to {0}'s manager.",
      "fist-bumps {0}... in the back of the head.",
      "creates a profile for {0} on gothicmatch.com",
    ]

    undirected = [
    'looks around for something to diss.',
    'steals your gpg keys.', 
    'performs a hostile IRC takeover.',
    'routes 1918 IP space.',
    'shuts down your BGP sessions.',
    'turns off the power in the office.',
    'causes a server outage.'
   ]
    def __init__(self):
        self.commands = { 'diss': self.doDiss }

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

    def doDiss(self, channel, user, args, irc=None):
        diss = random.choice(self.disses)
        return "/me " + diss.format(" ".join(args))

    def help(self, cmd):
        if cmd == 'diss':
            h = """Aw, DISS!"""
            return h

d = Disser()
