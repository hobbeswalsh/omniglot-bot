#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime, json, os, random, re, smtplib, sqlite3, urllib, urllib2, yaml
import time, twisted.names.client, xml.etree.ElementTree

from BeautifulSoup import BeautifulSoup as Soup
from xml.sax.saxutils import unescape, escape
from email.MIMEText import MIMEText
from twisted.internet import defer, reactor, protocol

class Commander(object):
    """A class that will take anything for an argument and try to execute it. 
    After execution, the behavior of this class should be fairly well-defined. 
    Either we return a string or we return nothing. 
    """

    def __init__(self, sso=None):
        self.ACTION_YML = os.getcwd() + "/data/action.yml"
        self.sso = sso

    def getCommand(self, cmd):
        try:
            return getattr(self, 'command_{0}'.format(cmd))
        except AttributeError:
            return None

    def callCommand(self, brain, name, args):
        cmd = self.getCommand(name)
        if cmd is None:
            return
        return cmd(brain, args)

    def setChannelLog(self, logfile):
        self.channel_log = logfile

    def getChannelLog(self):
        return self.channel_log

    def fetchUrl(self, url, post=None):
        if self.sso is None:

            return urllib2.urlopen(url).read()
        self.sso.install()
        return urllib2.urlopen(url, post).read()

    def command_help(self, brain, commands):
        """Really? http://lmgtfy.com/?q=help"""

        if not commands or not commands[0]:
            return self.generic_help()

        usages = [ self.get_usage(cmd) for cmd in commands ] 
        return "\n".join(usages)

    def generic_help(self):
        s = ""
        s += "Here are the commands I know about:\n"
        commands = list()
        l = dir(self)
        for item in l:
            if item.startswith("command_"):
                commands.append(item.replace("command_", ""))
        commands.sort()
        s += ", ".join(commands).strip() + "\n"
        s += "?help [command] will give you more detailed information.\n"
        return s

    def get_usage(self, cmd):

        try:
            command = getattr(self, 'command_{0}'.format(cmd))
        except AttributeError:
            return "no such command {0}".format(cmd)

        if (command) and (command.__doc__ is None):
            return "Please bug rwalsh@ to document {0}".format(cmd)

        return command.__doc__.strip()

    def command_monkey(self, brain, arg=None):
        """Prints a useful simian string"""

        if arg:
            return self.act(self.ACTION_YML, 'monkey', arg)
        else:
            return self.act(self.ACTION_YML, 'monkey', None)


    def command_bagel(self, brain, args):
        return 'ACTgets austin a bagel.'

    def command_host(self, brain, host):
        """this should resolve a hostname. currently in beta(tm)."""
        return

    def generate_dict(self, basedir):
        wtf_files = []
        wtf_dict = {}

        walker = os.walk(basedir)
        for d in walker:
            basedir = d[0]
            wtf_files.extend( [basedir + '/' + filename for filename in d[2]] )

        for wtf_file in wtf_files:
            f = open(wtf_file)
            for line in f:
                a = line.strip().split(None, 1)
                if not a:
                    continue
                key, value = a
                wtf_dict[key.lower()] = value

        return wtf_dict


    def act(self, yml, cmd, arg=None):
        y = yaml.safe_load(open(yml))

        if arg:
            choices = y[cmd]['directed']        
        else:
            choices = y[cmd]['undirected']

        action = choices[random.randint(0, len(choices)-1)].strip()

        if arg:
            action = action.replace("TARGET", " ".join(arg))

        return 'ACT' + action


    def _command_imdb(self, brain, arg):
        if arg is None:
            return
        q = "+".join(arg)
        url = "http://www.deanclatworthy.com/imdb/?q=" + q
        bigurl = 'http://www.imdb.com/title/'

        try:
            j = json.loads(self.fetchUrl(url))
        except ValueError:
            return
        title = j['title']
        rating = j['rating']
        url = j['imdburl']
        uri = url.rsplit('/')[-1]
        t = self.command_tiny(None, bigurl + uri)
        return "{0} ({1}) :: {2}".format(title, rating, t)

    def command_fortune(self, brain, arg):
        url = "http://www.iheartquotes.com/api/v1/random"
        newline = re.compile('[\n\r]')
        endline = re.compile('\[.*$')
        result = self.fetchUrl(url)
        reply = re.split(newline, result)[:-3]
        for n in range(0, reply.count('')):
            reply.remove('')
        return "\n".join(reply).replace("\t", "  ", 0)


    def command_pwnt(self, brain, arg):
        """You asked for it..."""

        brain._irc.kick('#dns-guru', 'austin', '?pwnt finally implemented')

    def command_props(self, brain, arg):
        """props <target> - Give hella props to someone/something!"""
        props = self.act(self.ACTION_YML, 'props', arg)
        return props


    def command_diss(self, brain, arg):
        """diss <target> - Hella diss someone/something!"""
        diss = self.act(self.ACTION_YML, 'diss', arg)
        return diss


    def command_feature(self, brain, arg):
        """feature <feature> request a feature! rwalsh will get around to it.... some day..."""

        f = open(os.getcwd() + "/data/features.txt", "a")

        f.write(" ".join(arg) + "\n")

    def command_beer(self, brain, args):
        """It's gotta be beer o'clock *somewhere*"""

        MST = ['Boulder, CO', 'Whitefish, MT', 'Flagstaff, AZ',
               'Casper, WY', 'Twin Falls, ID', 'Durango, CO',
               'Los Alamos', 'Grand Canyon National Park, AZ',
               'Aspen, CO', 'Thunder Basin National Grassland, WY']

        CST = ['Madison, WI', 'Springfield, IL', 'Kansas City, MO',
               'St. Cloud, MI', 'New Orleans, LA', 'Nashville, TN',
               'Tulsa, OK', 'Bismark, ND', 'Hueco Tanks, TX',
               'Buffalo Gap National Grassland, SD']

        EST = ['Acadia National Park, ME', 'Burlington, VT', 'New York, NY',
               'Savannah, GA', 'Roanoke, VA', 'Hoboken, NJ',
               'Franconia Notch, NH', 'Vanderwhacker Mountain, NY',
               'Philadelphia, PA' ]
        EUR = ['Rotterdam, Netherlands', 'Evian-les-bains, France',
               'Freiburg, Germany', 'Mallorca, Spain']

        tz_offsets = { 1: MST, 2: CST, 3: EST, 4: EUR, 5: EUR, 6: EUR }

        now = datetime.datetime.now()
        local_hour = now.hour
        if local_hour >= 17:
            return "It's beer o'clock already!"

        if (17 - local_hour) in tz_offsets:
            tz = tz_offsets[(17 - local_hour)]
            city = tz[random.randint(0, len(tz)-1)].strip()
            s = "It is definitely beer o' clock in {0}.".format(city)
            return s
        else:
            return "It's 5 o'clock somewhere..."

    def command_said(self, brain, args):
        """said [nick] [pattern] I'll search through the logs to see if [nick] has said [pattern]. Keep in mind that this is a SQL wildcard expression, and I search using %[pattern]%, so 'said rwalsh e' is probably not a good way to use this command."""
        if len(args) < 2:
            return 'Whatchoo talkin\' \'bout, Willis?'

        nick = args[0]

        try:
            throttle = 0 - abs(int(args[-1]))
            pattern = " ".join(args[1:-1])
        except ValueError:
            throttle = -3
            pattern = " ".join(args[1:])

        conn = sqlite3.connect(self.channel_log)
        c = conn.cursor()
        sql_cmd = """SELECT * from channels
                     WHERE nick LIKE ?
                     AND msg LIKE ?"""

        c.execute(sql_cmd,
                ("{0}%".format(nick),
                "%{0}%".format(pattern)))
        found = c.fetchall()
        c.close()

        ret = []
        for row in found[throttle:]:
            (id, ts, chan, nick, msg) = row
            ts = time.strftime('%m/%d %H:%M', time.localtime(ts))
            ret.append("[{0} {1}] {2}: {3}".format(ts, chan, nick, msg))

        return "\n".join(ret)

if __name__ == "__main__":
    import os, sys

    command = sys.argv[1]
    args = sys.argv[2:]

    c = Commander()
    ret = c.callCommand('brain', command, args)
    print ret

