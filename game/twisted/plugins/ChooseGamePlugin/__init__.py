from ServerSide import ChooseGamePlugin

try:
    from ClientSDL import ChooseGamePluginSDL
except:
    from twisted.python import log
    log.msg("SDL Client Plugin could not be loaded.")

try:
    from ClientAscii import ChooseGamePluginAscii
except:
    from twisted.python import log
    log.msg("Ascii Client Plugin could not be loaded.")
