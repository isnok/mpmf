#!/usr/bin/env python
""" Game Server Launcher """

##
#  Parse Commanline Args
##

from argparse import ArgumentParser

parser = ArgumentParser(description="Defender Server")
parser.add_argument(
    "-d", "--debug", help="debug foo"
)
parser.add_argument(
    "-v", "--verbose", action="store_true", default=False, help="be verbose"
)
parser.add_argument(
    "-l", "--log", type=str, default="-", help="logfile ('-' for stdout)"
)
parser.add_argument(
    "-p", "--port", type=int, default=3333, help="port to serve game(s) on"
)
parser.add_argument(
    "-i", "--interface", type=str, default='', help="interface to serve game(s) on"
)
args = parser.parse_args()

##
#  Configure
##

from twisted.python import log
if args.log in ("-", "stdout", "stdio"):
    import sys
    logTo = sys.stdout
else:
    from twisted.python.logfile import DailyLogFile
    logTo = DailyLogFile.fromFullPath(args.log)
log.startLogging(logTo)

if args.verbose:
    log.msg("Args: %s" % args)

from serverlib.gamehost import GameHostResource
g = GameHostResource(args)

##
#  Launch
##

g.startService()

from twisted.internet import reactor

reactor.run()
