from ServerSide import IdleGame

try:
    from ClientSDL import IdleClientSDL
except:
    from twisted.python import log
    log.msg("SDL Client Plugin could not be loaded.")

try:
    from ClientAscii import IdleClientAscii
except:
    from twisted.python import log
    log.msg("Ascii Client Plugin could not be loaded.")
