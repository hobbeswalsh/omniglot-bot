from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
from random import choice

class Address(object):
    implements(IPlugin, ICommandWatcher)

    insult_p1 = ['artless', 'bawdy', 'beslubbering', 'bootless', 'churlish',
    'cockered', 'clouted', 'craven', 'currish', 'dankish', 'dissembling', 
    'droning', 'errant', 'fawning', 'fobbing', 'froward', 'frothy', 
    'gleeking', 'goatish', 'gorbellied', 'impertinent', 'infectious', 
    'jarring', 'loggerheaded', 'lumpish', 'mammering', 'mangled', 'mewling',
    'paunchy', 'pribbling', 'puking', 'puny', 'qualling', 'rank', 'reeky', 
    'roguish', 'ruttish', 'saucy', 'spleeny', 'spongy', 'surly',
    'tottering', 'unmuzzled', 'vain', 'venomed', 'villainous', 'warped',
    'wayward', 'weedy', 'yeasty']

    insult_p2 = ['base-court', 'bat-fowling','beef-witted','beetle-headed', 
    'boil-brained', 'clapper-clawed', 'clay-brained', 'common-kissing', 
    'crook-pated', 'dismal-dreaming', 'dizzy-eyed', 'doghearted', 
    'dread-bolted', 'earth-vexing', 'elf-skinned', 'fat-kidneyed', 
    'fen-sucked', 'flap-mouthed', 'fly-bitten','folly-fallen', 'fool-born', 
    'full-gorged','guts-griping','half-faced','hasty-witted', 'hedge-born', 
    'hell-hated', 'idle-headed', 'ill-breeding', 'ill-nurtured', 
    'knotty-pated', 'milk-livered', 'motley-minded', 'onion-eyed', 
    'plume-plucked', 'pottle-deep', 'pox-marked', 'reeling-ripe', 
    'rough-hewn', 'rude-growing', 'rump-fed','shard-borne','sheep-biting', 
    'spur-galled', 'swag-bellied', 'tardy-gaited', 'tickle-brained', 
    'toad-spotted', 'unchin-snouted', 'weather-bitten']

    insult_p3 = ['apple-john', 'baggage', 'barnacle', 'bladder','boar-pig', 
    'bugbear', 'bum-bailey', 'canker-blossom', 'clack-dish', 'clotpole', 
    'coxcomb', 'codpiece', 'death-token', 'dewberry', 'flap-dragon', 
    'flax-wench', 'flirt-gill', 'foot-licker', 'fustilarian', 'giglet', 
    'gudgeon', 'haggard','harpy','hedge-pig','horn-beast', 'hugger-mugger', 
    'joithead', 'lewdster', 'lout', 'maggot-pie', 'malt-worm', 'mammet', 
    'measle', 'minnow', 'miscreant', 'moldwarp', 'mumble-news', 'nut-hook', 
    'pigeon-egg', 'pignut', 'puttock', 'pumpion', 'ratsbane', 'scut', 
    'skainsmate', 'strumpet', 'varlet', 'vassal', 'whey-face', 'wagtail']

    def __init__(self):
        self.commands = { 'address': self.getAddress }

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

    def getAddress(self, channel, user, args, irc=None):
        address = list()
        address.append("195 E 4th Ave. (2nd floor)")
        address.append("San Mateo, CA 94401")
        insult = [ choice(l) for l in (insult_p1, insult_p2, insult_p3) ]
        insult_1 = choice(self.insult_p1)
        insult_2 = choice(self.insult_p2)
        insult_3 = choice(self.insult_p3)
        address.append("...thou " + ", ".join(insult))
        return address

    def help(self, cmd):
        if cmd == 'address':
            h = """Wait, what's Wordnik's address again?"""
            return h

a = Address()
