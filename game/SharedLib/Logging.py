from twisted.python import log
from SharedLib.Interfaces import IMainSetup

args = IMainSetup("string")
if args.log == "-" and hasattr(args, "ascii") and args.ascii:
    args.log = '/dev/null'
if args.log in ("", "-", "stdout", "stdio"):
    import sys
    logTo = sys.stdout
else:
    from twisted.python.logfile import DailyLogFile
    logTo = DailyLogFile.fromFullPath(args.log)
log.startLogging(logTo)

from pprint import pformat

if args.debug or args.verbose:
    log.msg("Startup args:\n%s" % pformat(vars(args)))
