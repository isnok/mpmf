#!/usr/bin/env python

from clientlib.tools import color, output
import random

client_frontends = [ 'sdl', 'ascii' , 'admin' ]

def parse_cmdline():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Defender Client Launcher")
    parser.add_argument("-f", "--frontend", default='sdl', help="frontend type (one of: %s)" % client_frontends)
    parser.add_argument("-r", "--resolution", default='1024x768', help="resolution like '1024x768'")
    parser.add_argument("-F", "--fullscreen", action='store_true', default=False, help="fullscreen mode")
    parser.add_argument("-c", "--coordinates", default='0x0', help="window position like '300x200'")
    parser.add_argument("-u", "--username", default='guest%s' % str(random.randrange(100000,999999)), help="username")
    parser.add_argument("-p", "--password", default=None, help="password")
    parser.add_argument("-H", "--host", default='localhost', help="server host")
    parser.add_argument("-P", "--port", default='3333', help="server port")
    parser.add_argument("-g", "--game", default='sdlplay', help="game name")
    parser.add_argument("-l", "--log", default='/dev/null', help="logfile (ascii version only)")
    parser.add_argument("-d", "--debug", action="store_true", help="debug mode")
    args = parser.parse_args()
    return args

def run(args):

    if args.debug:
        debug = True
    else:
        debug = False

    output('arguments', 'debug', args, source='client.py')
    output('frontend: %s' % args.frontend, 'debug', source='client.py')
    output('resolution: %s' % args.resolution, 'debug', source='client.py')
    output('position: %s' % args.coordinates, 'debug', source='client.py')
    output('credentials: %s' % args.username, 'debug', source='client.py')

    if args.frontend == 'sdl':
        from threading import Thread
        from clientlib.Connection import Connection
        import Queue
    
        output('starting connection-/server-thread', 'debug', source='client.py')
        server_queue = Queue.Queue()
        command_queue = Queue.Queue()
        
        connection_arguments = (server_queue, command_queue, args.host, args.port, args.game, args.username, args.password, debug)
        connection_thread = Thread(target=Connection, name='connectionThread', args=connection_arguments)
        connection_thread.start()

        from clientlib.sdl import Play
        play = Play(server_queue, command_queue, args, debug)

    elif args.frontend == 'ascii':
        from clientlib.ascii import Play
        play = Play(args, debug)

    elif args.frontend == 'admin':
        from clientlib.admin import Play
        play = Play(args, debug)

    else:
        output('Unknown Frontend type: %s' % args.frontend, 'error', 'client.py')

    output('Starting game class', 'debug', source='client.py')

    play.gameloop()

    if args.frontend == 'sdl':
        output('Trying to stop connection Thread', 'debug', source='client.py')
        connection_thread._Thread__stop()
    
    output('Game class finished', 'debug', source='client.py')

if __name__ == "__main__":

    import Queue
    global update_queue, debug

    update_queue = Queue.Queue()
    commands = Queue.Queue()
    debug = False

if __name__ == "__main__":

    run(parse_cmdline())
