mpmf
====

More Players, More Fun!

mpmf seems to become a framework, to make multiplayer games.
It features hotplugging of new games into the server and client
at run time and heavy (up to extreme) code reuse.  It's also my
first try on zope/twisted component structure, if you know what
IMean.

Installing
----------

The main dependencies of mpmf are python >= 2.6 and twisted for
the server, additionally for the client either the python curses
module or pygame.
The game folder contains a Makefile, that gives some hints on how
to install required packages/dependencies on a debian system.


Running
-------

Navigate to the game folder and start up a server, that logs to
stdout, via:

$ ./serve.py

You can then already visit this server with a browser, if you navigate to:
http://localhost:3333/

To start a client use

$ ./play.py

for a pygame client, or

$ ./play.py -a -l /tmp/ascii.log

for an ascii client, that logs to /tmp/ascii.log .

You can also use the convenience make targets
 * clean - remove pyc files and plugin caches (default)
 * serve - start a server in the background if needed
 * watch - attach to the servers log
 * ascii - start a server and an ascii client
 * sdl - start a server and an sdl client

Playing
-------

Both clients can be quit by pressing q, and maybe Escape.
The pygame/sdl client is controlled with the mouse by clicking.
The curses/ascii client is controlled via h/j/k/l and space for clicking.

What's next?
------------

I'm still framing this out, to make a nice tower defense!
