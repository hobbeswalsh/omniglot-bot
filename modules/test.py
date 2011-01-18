#!/usr/bin/env python
import sys
sys.path.append('.')

from twisted.plugin import getPlugins
from interfaces import IMessageWatcher
#from twisted.plugins.imessagewatcher import IMessageWatcher


if __name__ == "__main__":
    cmds = getPlugins(IMessageWatcher)
    for cmd in cmds:
        print cmd.gotMsg("hello")
