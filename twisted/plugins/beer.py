from zope.interface import implements, classProvides
from twisted.plugin import IPlugin

from modules.interfaces import *
import json, random, time, urllib2

class BeerDB(object):
    implements(IPlugin, ICommandWatcher)

    baseurl = "http://obdb-dev-hoke.apigee.com/"
    prefixes = [
        "/me feels like a ",
        "how about a ",
        "Yum... a delicious ",
        "/me could use a ",
        "/me is thinking about ",
        "/me suggests ",
    ]

    def __init__(self):
        self.commands = { 'beer': self.getBeer }

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

    def getBeer(self, channel, user, args, irc=None):
        uri = "beers/count"
        url = self.baseurl + uri
        j = json.loads(urllib2.urlopen(url).read())
        numBeers = j['count']
        beerId = random.randint(0, numBeers)

        uri = "beers/get?id={0}".format(beerId)
        url = self.baseurl + uri
        j = json.loads(urllib2.urlopen(url).read())
        beerName = j[0]['name']
        breweryId = j[0]['brewery_id']

        uri = "breweries/get?id={0}".format(breweryId)
        url = self.baseurl + uri
        j = json.loads(urllib2.urlopen(url).read())
        breweryName = j[0]['name']

        ret = "{0} from {1}".format(beerName,breweryName)
        print ret
        return random.choice(self.prefixes) + ret

    def help(self, cmd):
        if cmd == 'beer':
            h = """Fetch a random beer! Yum!"""
            return h

bdb = BeerDB()
