# -*- coding: utf-8 -*-
from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import os, random

class Disser(object):
    implements(IPlugin, ICommandWatcher)

    propses = [
     "sings a power-ballad about {0}.",
     "writes an epic poem about {0}.",
     "thinks that {0} is pretty darn cool.",
     "nominates {0} for the Nobel Prize in Awesome.",
     "recognizes the intrinsic value of {0}.",
     "puts 50 cents in {0}'s tip jar.",
     "and {0} are like, totally BFF.",
     "sings {0}'s accolades from the highest mountaintops.",
     "gives {0} a cookie.",
     "defers to {0}'s linguistic prowess.",
     "consults {0} when he can't find a dictionary.",
     "can't wait to grow up and be more like {0}.",
    ]

    undirected = [
     "gives you a high-five.",
     "fist-bumps you.",
     "winks knowingly at you.",
     "buys you a drink.",
     "picks up a coffee for you at Peet's.",
     "buys you a book.",
     "looks up 'rad' in the dictionary and sees your portrait.",
    ]

    def __init__(self):
        self.commands = { 'props': self.doProps }

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

    def doProps(self, channel, user, args, irc=None):
        if len(args) == 0:
            props = random.choice(self.undirected)
            return "/me " + props.format(" ".join(args))

        props = random.choice(self.propses)
        return "/me " + props.format(" ".join(args))

    def help(self, cmd):
        if cmd == 'props':
            h = """Props bro!"""
            return h

d = Disser()
