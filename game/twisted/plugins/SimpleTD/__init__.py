from ServerSide import SimpleTD

try:
    from ClientSDL import SimpleTDClientSDL
except:
    from twisted.python import log
    log.msg("SDL Client Plugin could not be loaded.")

try:
    from ClientAscii import SimpleTDClientAscii
except:
    from twisted.python import log
    log.msg("Ascii Client Plugin could not be loaded.")
