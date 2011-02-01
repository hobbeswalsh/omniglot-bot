# -*- coding: utf-8 -*-
from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import os, random, yaml

class Monkey(object):
    implements(IPlugin, ICommandWatcher, IMessageWatcher)

    monkeywords = [
        'monkey',
        'monkeys',
        'monkeying',
        'gorilla',
        'gorillas',
        'banana',
        'bananas',
        'simian',
        'chimp',
        'chimps',
        'chimpanzee',
        'chimpanzees',
        'ape',
        'apes',
    ]

    undirected = [
        "/me hides raisins about the premises.",
        "/me swings from his simian tail.",
        "/me goes 'eek eek!'",
        "/me eats a banana.",
    ]

    directed = [
        "/me flings poo at {0}.",
        "/me shrieks at {0}.",
        "/me picks lice from {0}'s hair.",
        "/me gives {0} a banana.",
        "/me smiles menacingly at {0}.",
    ]


    def __init__(self):
        self.commands = { 'monkey': self.doMonkey }

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

    def gotMsg(self, channel, user, msg, irc=None):
        msgwords = msg.split()
        for word in msgwords:
            if word in self.monkeywords:
                return random.choice(self.undirected)

    def doMonkey(self, channel, user, args, irc=None):
        if len(args) == 0:
            return random.choice(self.undirected)

        else:
            monkey = random.choice(self.directed)
            return monkey.format(" ".join(args))

    def help(self, cmd):
        if cmd == 'monkey':
            h = '''"I told you, never trust a monkey!"'''
            return h

m = Monkey()
