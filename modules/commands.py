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

    def _command_page(self, brain, args):
        """page <username> <message> - I'll page <username> with <message>...  assuming you've got rights to send out pages. Don't abuse this tool. Don't, really."""

        if not args:
            print "NOOOOOOOOO"
            return

        message = ' '.join(args)
        try:
            (person, message) = message.split(' ', 1)
        except ValueError:
            print "You need to tell me who to page and what to say!"
            return

        mail_server = 'smarthost.yahoo.com'
        recipient = 'page-' + person + '@yahoo-inc.com'
        sender = 'dnsbot@yahoo-inc.com'

        msg = MIMEText(message)
        msg['Subject'] = 'page from IRC'

        s = smtplib.SMTP()
        s.connect(mail_server)
        s.sendmail(sender, recipient, msg.as_string())

        print "I just paged {0}!".format(recipient)



    def command_blog(self, brain, arg):
        """blog <regex> Gets the list of current entries on the SA blog, which will usually correspond (more or less) to pages our outages. Optional <regex> flag will specify a regex to search for in the titles of the blog entries."""

        pattern =  "".join(arg)
        blog_re = re.compile('.*%s.*' % pattern, re.I)

        url = "http://sa.seoblogs.ops.yahoo.net/feed/"

        content = self.fetchUrl(url)

        rss = xml.etree.ElementTree.fromstring(content.read())

        channel = rss.find("channel")

        l = []
        for item in channel.getiterator("item"):
            if not re.search(blog_re, item[0].text):
                continue

            title = item[0].text.strip()
            tiny = self.command_tiny(None, item[1].text.strip())

            l.append("{0} :: {1}".format(title.encode('ascii','ignore'),tiny))

        return "\n".join(l)

    def command_unowned(self, brain, args):

        """I'll go find out how many unowned Siebel tickets are in the DNS queue and how many NSS Traffic Management bugs belong to dns-guru."""

        s_web_url = "http://yoc.yahoo.com/cgi-bin/siebel-api.cgi?b=ops&s=Assigned&o=dns-ops-tickets"
        s_url = "http://tickets-rss.ops.yahoo.com/feeds/opsamericas/DNS/allunassigned.rss"

        rss = xml.etree.ElementTree.fromstring(self.fetchUrl(s_url))
        s_unowned = rss.findall('{http://purl.org/rss/1.0/}item')

        ## ACK!
        bug_www_url = """http://bug.corp.yahoo.com/buglist.cgi?bug_file_loc_type=allwordssubstr&bug_status=NEW&bug_status=ACCEPTED&bug_status=REOPENED&bugidtype=include&chfieldto=Now&component=DNS%20-%20General&component=DNS%20-%20Hardware&component=DNS%20-%20M%26A&component=DNS%20-%20Monitoring&component=DNS%20-%20Servfail&component=DNS%20-%20Trackers&component=DNS%20-%20ynamed&emailassigned_to1=1&emailassigned_to2=1&emailcc1=1&emailcc2=1&emailqa_contact1=1&emailqa_contact2=1&emailreporter2=1&emailtype1=substring&emailtype2=substring&field0-0-0=assigned_to&field0-0-1=assigned_to&field0-0-2=assigned_to&field0-0-3=noop&field0-0-4=noop&field0-0-5=noop&keywords_type=allwords&long_desc_type=substring&product_name=Operations%20-%20Traffic%20Management%20Team&query_format=advanced&short_desc_type=allwordssubstr&status_whiteboard_type=allwordssubstr&type0-0-0=equals&type0-0-1=equals&type0-0-2=equals&type0-0-3=noop&type0-0-4=noop&type0-0-5=noop&value0-0-0=dns-guru%40yahoo-inc.com&value0-0-1=tps%40yahoo-inc.com&value0-0-2=dns-devel%40yahoo-inc.com&value0-0-3=kreddy%40yahoo-inc.com&value0-0-4=jmanning%40yahoo-inc.com&value0-0-5=johneagl%40yahoo-inc.com"""

        bug_xml_url = bug_www_url + "&ctype=rss"

        ug = self.fetchUrl(bug_xml_url)
        bugrss = xml.etree.ElementTree.fromstring(ug)
        bug_unowned = bugrss.findall('{http://www.w3.org/2005/Atom}entry')

        ret = "%-2s unowned siebel tickets :: %s" % (len(s_unowned), self.command_tiny(None, s_web_url))
        ret += "\n%-2s unowned bugs           :: %s" % (len(bug_unowned), self.command_tiny(None, bug_www_url))

        return ret

    def command_dnsq(self, brain, arg):
        """dnsq <regex> I'll go get a list of unowned tickets in the DNS queue and spew 'em out. I recommend you use the optional <regex> to narrow down your search by ticket title."""

        pattern =  "".join(arg)
        siebel_re = re.compile('.*%s.*' % pattern, re.I)

        url = "http://tickets-rss.ops.yahoo.com/feeds/opsamericas/DNS/allunassigned.rss"

        rss = xml.etree.ElementTree.fromstring(self.fetchUrl(url))
        ticketlist = rss.findall('{http://purl.org/rss/1.0/}item')

        l = list()
        for ticket in ticketlist:
            if not re.search(siebel_re, ticket[0].text):
                continue

            title = ticket[0].text.strip()
            tinyurl = self.command_tiny(None, ticket[1].text.strip())

            l.append("%s :: %s" % (title, tinyurl))

        return "\n".join(l).strip()

    def command_bug(self, brain, args):
        """bug <bug number> will give you information about the given bug."""

        ## API info @:
        ## http://twiki.corp.yahoo.com/view/Bugzilla/BugzillaWebServicesConfig

        if not args:
            return

        fmt = 'json'
        data = 'basic'
        bugnum = args[0].strip()

        url = "http://api.bug.corp.yahoo.com:4080/"

        key_uri = "api/1/wssid/{0}".format(fmt)
        j = json.loads(self.fetchUrl(url + key_uri))
        key = j['WSSID']

        bug_uri = "api/1/bugs/{0}/{1}/{2}/{3}".format(bugnum,fmt,data,key)
        bugjson = json.loads(self.fetchUrl(url + bug_uri))

        ## There's an uncaught exception here if the URL is bad
        ## (i.e. if someone gives a bogus bug number)

        id = bugjson['id']
        desc = bugjson['short_desc']

        bug_www_url = "http://bug.corp.yahoo.com/"
        bug_www_uri = "show_bug.cgi?id={0}".format(id)
        tiny = self.command_tiny(None, bug_www_url + bug_www_uri)
        return "{0} :: {1}".format(desc, tiny)


    def command_siebel(self, brain, ticketnum):
        """siebel <siebel ticket #> will display some information about the siebel ticket."""

        if not ticketnum:
            return

        s_url = "http://yoc.yahoo.com/cgi-bin/siebel-ticket.cgi?ticket="
        url = s_url + ticketnum[0]

        soup = Soup(self.fetchUrl(url))
        td = soup.findAll('td')
        if len(td) < 10:
            return

        title = td[9].string

        return "{0} :: {1}".format(title, self.command_tiny(None, url))

    command_s = command_siebel
    command_stupid_effing_ticket_system = command_siebel

    def command_bagel(self, brain, args):
        return 'ACTgets austin a bagel.'

    def command_host(self, brain, host):
        """this should resolve a hostname. currently in beta(tm)."""
        return

    def command_by(self, brain, args):
        if not args:
            return

        url = "http://search.corp.yahoo.com/"
        uri = "ws.php?app=backyard&search=employee&format=json&hits=150&query={0}"

        query = "%20".join(args)
        ret = []
        u = url + uri.format(query)
        try:
            j = json.loads(self.fetchUrl(u))
        except ValueError:
            return "No dice. Try narrowing the search."

        if len(j['docs']['employee']) == 1:
            ## we only found one employee. this is good!
            return self.format_employee(j['docs']['employee'][0])
        if len(j['docs']['employee']) > 1:
            employees = j['docs']['employee']
            relevant = [ e for e in employees if e['relevancy'] > 1000 ]
            ret = [ self.short_format_employee(e) for e in relevant ]
            return ", ".join(ret)

    def format_employee(self, e):
        s = ""
        s += "Name      : {0}\n".format(e['employeename'])
        s += "UserID    : {0}\n".format(e['userid'])
        s += "Department: {0}\n".format(e['dfdept'])
        s += "Manager   : {0}\n".format(e['managername'])
        s += "YIM ID    : {0}\n".format(e['yahooid'])
        s += "Phone     : {0}\n".format(e['phonenum'])
        s += "Link      : {0}".format(self.command_tiny('', e['uri']))
        return s

    def short_format_employee(self, e):
        return "{0} ({1})".format(e['employeename'], e['userid'])

    def command_tiny(self, brain, arg):
        return "http://www.wordnik.com"

    def command_cm(self, brain, arg):
        """cm <expression> If <expression> looks like a CMR number, I'll try to find the description of that CMR for you. If not, I'll search through all currently running CMRs and search for <expression> in the title. E.g. 'cm mud' would give you a list of all currently running CMRs in MUD. If you omit <expression> you'll get a list of all currently running CMRs. Please don't make me spam IRC."""

        pattern =  "".join(arg)
        cm_re = re.compile('.*%s.*' % pattern, re.I)

        ret = []
        ## URL to find all currently running CMRs.
        url = "http://api.cm.ops.yahoo.com/feed/xml/"
        ## Base web URL
        wurl = 'http://cm.ops.yahoo.com/requests.php?action=viewrequest&cmr_id='

        ## different URL if we're searching by CM number
        if re.match('^[\d]+$', pattern):
            url += "?cmr_id={0}".format(pattern)
        else:
            url += "?cmr_status=started"
        

        rss = xml.etree.ElementTree.fromstring(self.fetchUrl(url))

        for item in rss.getchildren():
            cm_properties = item.getchildren()
            pnum = 0
#            for prop in cm_properties:
#                print "{0} {1} ({2})".format(prop, prop.text, pnum)
#                pnum += 1
            p = cm_properties
            cmr_id, type, status, title, start, end, risk = p[0].text, p[3].text, p[4].text, p[11].text, p[13].text, p[14].text, p[29].text
            if ( (cmr_id != pattern) and (not cm_re.match(title)) ):
                continue
            cm_url = self.command_tiny(None, wurl + cmr_id)
            s = "{0} ({1}) :: {2}\n".format(title, risk, cm_url)
            s += "{0} - {1} ({2}, {3})".format(start, end, type, status)
            ret.append(s)

        return "\n".join(ret)
        
    ## cheap alias
    command_cmr = command_cm

    def command_bro(self, brain, args):
        bro_host="api.test.brooklyn.ops.yahoo.com"
        bro_port = "4080"
        bro_uri = "rest/v1/BrooklynRequest.find"
        bro_url = "http://{0}:{1}/{2}".format(bro_host, bro_port, bro_uri)

        w_url = "http://brooklyn.ops.yahoo.com/request.php?action=viewrequest&request_id={0}"

        s = ""
        for arg in args:
            turl = self.command_tiny(None, w_url.format(arg))
            if arg == 'pending' or arg == 'accepted':
                url = bro_url + "?status={0}&output=json".format(arg)
                string = self._getBrooklynRequest(url)
                s += "{0} :: {1}".format(string, turl)
                continue
            try:
                int(arg)
            except:
                continue
            ## we are looking for a specific request
            url = bro_url + "?request_id[]={0}&output=json".format(arg)
            string = self._getBrooklynRequest(url)
            s += "{0} :: {1}".format(string, turl)
                
        return s

    def _getBrooklynRequest(self, url):
        s = ""
        r = self.fetchUrl(url)
        try:
            j = json.loads(r)
        except:
            pass
        if 'result' in j:
            results = j['result']
            for result in results:
                action = result['request_action']
                name = result['rotation_name']
                contact = result['contact']
                prop = result['property_name']
                s += "{0} {1} ({2}, {3})\n".format(action,name,contact,prop)
        return s


    def command_outage(self, brain, args):
        """outage <expression> I'll go and get the current list of open outages from ems.ynoc. I highly recommend using <expression> (regex or outage number), otherwise I'll spew all open outages back at you."""

        wurl = "http://ems.ynoc.yahoo.com/ops_ems/incident.php?action=view&id="

        api_url = "http://api.ems.ynoc.yahoo.com:4080/rest/V1/Incident.Search"

        x = """<request><criteria><incident_id>{0}</incident_id></criteria><columns><col>title</col><col>severity</col><col>status</col></columns></request>""".format(" ".join(args))

        post = urllib.urlencode( { 'data': x } )
        ret = xml.etree.ElementTree.fromstring(self.fetchUrl(api_url, post))

        title = ret.find('incidents/item/title').text
        id = ret.find('incidents/item/incident_id').text
        sev = ret.find('incidents/item/severity').text
        status = ret.find('incidents/item/status').text

        turl = self.command_tiny(None, wurl + id)
        return "{0} ({1} {2}) :: {3}".format(title, sev, status, turl)

    ## cheap alias
    command_ems = command_outage

    def command_metrics(self, brain, args):
        ## XXX wow, does this need work...
        """metrics <username username...> I'll show you how many siebel tickets usernames closed last week. If you omit the optional username argument, I'll give you a default list."""

        if not args:
            users = ['asmall', 'jmanning', 'pettit', 'rwalsh']
        else:
            users = args

        today = datetime.date.today()
        (y1, m1, d1) = (today.year, today.month, today.day)
        weekAgo = today - datetime.timedelta(weeks=1)
        (y2, m2, d2) = (weekAgo.year, weekAgo.month, weekAgo.day)

        bug_url = """http://bug.corp.yahoo.com/buglist.cgi?bug_file_loc_type=allwordssubstr&bug_status=RESOLVED&bugidtype=include&chfield=resolution&chfieldfrom=1w&chfieldto=Now&chfieldvalue=FIXED&component=DNS - General&component=DNS - Hardware&component=DNS - M&A&component=DNS - Monitoring&component=DNS - Servfail&component=DNS - Trackers&component=DNS - ynamed&email1=%s&emailassigned_to1=1&emailtype1=substring&emailtype2=substring&field0-0-0=noop&keywords_type=allwords&long_desc_type=allwordssubstr&product_name=Operations - Traffic Management Team&query_format=advanced&resolution=FIXED&short_desc_type=allwordssubstr&status_whiteboard_type=allwordssubstr&ctype=rss"""

        siebel_url = """http://yoc.yahoo.com/cgi-bin/siebel-api.cgi?r2=%s-%s-%s&r1=%s-%s-%s&b=ops&s=Closed&o=%s"""
        ret = []
        for user in users:

            s_url = siebel_url % (y1, m1, d1, y2, m2, d2, user)
            b_url = bug_url % user
            b_url = b_url.replace(' ', '%20').replace('M&A', 'M%26A')

            soup = Soup(self.fetchUrl(s_url))
            rss = xml.etree.ElementTree.fromstring(self.fetchUrl(b_url))
            m = len(soup.findAll('a', target='_tkt', href=re.compile('[\d]$')))
            n = len(rss.findall('{http://www.w3.org/2005/Atom}entry'))

            ret.append("last week %s closed: %-2d siebel, %-2d bugzilla"%(user,m,n))

        return "\n".join(ret)

        
    def command_roles(self, brain, args):
        """roles <hostname> will return a list of roles a hostname is in."""

        if not args:
            return

        l = [ self._get_roles(host) for host in args ]

        return "\n".join(l)

    ## helper function
    def _get_roles(self, host):

        if host.endswith('.yahoo.com'):
            fqdn = host
            host = fqdn.replace('.yahoo.com', '')
        else:
            fqdn = host + '.yahoo.com'

        url = "http://igor.corp.yahoo.com/igor/api/getHostRoles?host=%s"%fqdn

        rss = xml.etree.ElementTree.fromstring(self.fetchUrl(url))
        roles = rss.findall('set')[0].getchildren()
        rnames = ['{0}: '.format(host) + role.attrib['name'] for role in roles]
        return "\n".join(rnames)


    def command_members(self, brain, args):
        """members <rolename> will get a list of hosts in a role."""

        if not args:
            return

        l = [ self._get_members(role) for role in args ]

        return "\n".join(l)

    ## helper function
    def _get_members(self, role):

        url = "http://igor.corp.yahoo.com/igor/api/getRoleMembers?role=%s"%role
        rss = xml.etree.ElementTree.fromstring(self.fetchUrl(url))
        hosts = rss.findall('role/members')[0].getchildren()
        hostnames = [host.attrib['name'] for host in hosts]
        reply = [ '{0}: '.format(role) + h for h in hostnames ]

        return "\n".join(reply)

    def command_rules(self, brain, args):
        """rules <rolename> will get a list of rules for a given role."""

        if not args:
            return

        role = args[0]

        url = "http://igor.corp.yahoo.com/igor/api/getRoleRules?role=%s" % role
        rss = xml.etree.ElementTree.fromstring(self.fetchUrl(url))
        rules = rss.findall('role/rules')[0].getchildren()
        rules_list = [ (rule.text or "") for rule in rules]

        return "\n".join(rules_list)

    def command_wtf(self, brain, args):
        """wtf <string> If I can find any information on <string> I'll let you know."""

        if not args:
            return
        response = []

        basedir = '/home/y/share/wtf'
        wtf_dict = self.generate_dict(basedir)
        for arg in args:
            if arg.lower() in wtf_dict:
                response.append("{0}: {1}".format(arg, wtf_dict[arg.lower()]))

        return "\n".join(response)

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


    def command_bkln_oncall(self, brain, args):
        """I'll tell you who's on call now and next for brooklyn."""

        url = "http://monitoring.bkln.corp.yahoo.com:9999/pager/gen-pager.cgi?both=1"
        oncall_csv = self.fetchUrl(url).split("\n")[0]
        primary, secondary = oncall_csv.split(',')
        
        l = []
        by_url = "http://api.backyard.yahoo.com/V1/GetUser?user_id="
        for i in (primary, secondary):
            if i == 'dns':
                l.append("{0} : {1}".format('page-prod-dns-tier3', 'XXX'))
                continue
            by_text = self.fetchUrl("{0}".format(by_url + i))
            by_xml = xml.etree.ElementTree.fromstring(by_text)
            cell = by_xml.find('cell_phone')
            l.append("{0} : {1}".format(i, cell.text))
        
        if l[0] == l[1]:
            return l[0]

        return "\n".join(l)

    def command_oncall(self, brain, args=None):
        """I'll tell you who's oncall now and who's on deck."""

        url = "http://isops1.corp.yahoo.com/pager?list=prod-dns-tier3&func=cal"

        soup = Soup(self.fetchUrl(url))
        tds = soup.findAll('td')

        current = tds[4].contents[0]
        until1 = tds[2].contents[0][5:-4]
        next = tds[9].contents[0]
        until2 = tds[7].contents[0][5:-4]

        suckers = [current, next]

        by_url = "http://api.backyard.yahoo.com/V1/GetUser?user_id="
        for i in range(0, len(suckers)):
            by_text = self.fetchUrl("{0}".format(by_url + suckers[i]))
            by_xml = xml.etree.ElementTree.fromstring(by_text)
            cell = by_xml.find('cell_phone')
            try:
                suckers[i] += " {0}".format(cell.text)
            except AttributeError:
                pass
            if "rwalsh" in suckers[i]:
                suckers[i] += " GRR!! D: D:"


        months = {1: 'Jan',
                  2: 'Feb',
                  3: 'Mar',
                  4: 'Apr',
                  5: 'May',
                  6: 'Jun',
                  7: 'Jul',
                  8: 'Aug',
                  9: 'Sep',
                  10: 'Oct',
                  11: 'Nov',
                  12: 'Dec' }

        s = ""
        s += "Now          -> {0} {1}\n".format(until1, suckers[0])
        s += "{0} -> {1} {2}".format(until1, until2, suckers[1])
        return s

    def command_alerts(self, brain, args):
        """alerts <hostname> - I'll try to find alert history information on the host you're asking about. This command doesn't ssh anywhere; it just checks the nagios console."""

        if not args:
            return

        host = args[0]

        if not host.endswith(".yahoo.com"):
            host = host + ".yahoo.com"

        if host.startswith("a"):
            cluster = "dns.auths"
        else:
            cluster = "dns.resolvers"

        url = "http://dnsmon1.ymon.corp.sp2.yahoo.com:9999/nagios/%s/cgi-bin/history.cgi?host=%s" % (cluster, host)

        if host.find('corp') > -1:
            cluster = 'DNS-CORP'
            url = "http://dnscorp.ymon.corp.ac4.yahoo.com:9999/nagios/%s/cgi-bin/history.cgi?host=%s" % (cluster, host)


        soup = Soup( self.fetchUrl )

        alerts = soup.findAll('div')[-1].findAll(text = re.compile('ALERT'))

        if len(alerts) == 0:
            return

        alert_re = re.compile(r"""
            (\[.*\]).*:     ## timestamp
            (.*?);          ## hostname
            (.*?);          ## alert name
            (.*?);          ## status (WARNING/CRITICAL, etc)
            (.*?);          ## type (HARD/SOFT)
            (.*?);          ## number of times alerted
            (.*?)$          ## return message from check
            """, re.VERBOSE)

        s = "{0}:\n".format(host)
        for alert in alerts:
            (time, hn, alrtnam, stats, typ, num, msg) = re.findall(alert_re, alert)[0]
        
            s +=  "{0}: {1}\n".format(time, msg)

        return s

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

