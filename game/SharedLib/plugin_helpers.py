from twisted.python import log
from twisted.plugin import IPlugin
from twisted.plugin import getPlugins

try:
    from ServeLib.Interfaces import IServerPlugin

    def getServerGames():
        return list(getPlugins(IServerPlugin))

except:
    log.msg("Cannot serve IServerPlugins.")


from SharedLib.Interfaces import IMainSetup
args = IMainSetup(-1)


try:
    from ClientLib.Interfaces import IClientPlugin

    def getClientGames(client=None):
        if args.ascii:
            from ClientLib.Interfaces import IAsciiFrontend
            games = dict([(p.plays, p) for p in getPlugins(IClientPlugin) if IAsciiFrontend.providedBy(p)])
            from ClientLib.curses_ascii.ChooseGameAscii import ChooseGameAscii
            games['ChooseGame'] = ChooseGameAscii
        else:
            from ClientLib.Interfaces import ISDLFrontend
            games = dict([(p.plays, p) for p in getPlugins(IClientPlugin) if ISDLFrontend.providedBy(p)])
            from ClientLib.pygame_sdl.ChooseGameSDL import ChooseGameSDL
            games['ChooseGame'] = ChooseGameSDL

            log.msg("SDLers: %s" % list(getPlugins(ISDLFrontend)))
            for name, plug in games.items():
                try:
                    log.msg("SDLer: %s %s" % (name, ISDLFrontend.providedBy(plug)))
                except:
                    log.msg("Error: %s %s" % (name, ISDLFrontend.providedBy(plug)))
        return games
except:
    log.msg("Cannot serve IClientPlugins.")
