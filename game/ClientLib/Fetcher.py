from twisted.python import log
from zope.interface import implements
from twisted.internet import reactor
from twisted.application.service import Service
from SharedLib.component_hacks import NamedAdapter
from ClientLib.Interfaces import IWebWorld
from twisted.internet.defer import Deferred
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Protocol
from twisted.web.client import HTTPConnectionPool
from twisted.web.client import Agent
from twisted.web.client import CookieAgent
from cookielib import CookieJar

http_pool = HTTPConnectionPool(reactor, persistent=True)
http_pool.maxPersistentPerHost = 1

class BodyReturner(Protocol):

    def __init__(self, finished, verbose=False):
        self.finished = finished
        self.received = ""
        self.verbose = verbose

    def dataReceived(self, bytes):
        self.received += bytes

    def connectionLost(self, reason):
        """ todo: test if reason is twisted.web.client.ResponseDone """
        if self.verbose:
            log.msg('Finished receiving body:', reason.getErrorMessage())
        self.finished.callback(self.received)

import json
import urllib
from pprint import pformat
from ClientLib.Interfaces import IDrawingEngine
from SharedLib.component_hacks import registerGlobal
from twisted.web.http_headers import Headers

class Fetcher(Service, NamedAdapter):

    implements(IWebWorld)

    def __init__(self, client):
        NamedAdapter.__init__(self, client)
        self.url = "http://%(host)s:%(port)s/play/%(game)s/json%%s" % vars(self.config)
        self.log("Fetching from: %s" % self.url)
        self._loop = LoopingCall(self.update)
        self.interval = 0.11
        self.agent = CookieAgent(Agent(reactor, pool=http_pool), CookieJar())
        self.verbose = client.config.verbose
        self.debug = client.config.debug
        registerGlobal(self, IWebWorld)

    def startService(self):
        if not self.running:
            self._loop.start(self.interval)
        Service.startService(self)

    def stopService(self):
        if self.running:
            self._loop.stop()
        Service.stopService(self)

    def update(self, args=None):
        headers = None
        body = None
        url = self.url % ""
        if args is not None:
            url = self.url % "?"
            url += urllib.urlencode(args)
            headers = Headers({'content-type': ['application/x-www-form-urlencoded']})
            self.log("Args fetch: %s" % url)
        if self.verbose:
            self.log("Fetch %s" % url)
        return self.agent.request(
                'GET', url, headers, body
            ).addCallback(
                self.fetched
            ).addErrback(
                self.err
            ).addErrback(
                lambda _: reactor.stop()
            )


    def logLoaded(self, data):
        self.log("Loaded response:\n%s" % pformat(data))
        return data

    def fetched(self, response):
        d = Deferred()
        response.deliverBody(BodyReturner(d, verbose=self.verbose))
        d.addCallback(json.loads)
        if self.verbose or self.debug:
            d.addBoth(self.logLoaded)
        return d.addCallback(IDrawingEngine(self).update)

from ClientLib.Interfaces import IClient
from twisted.python.components import registerAdapter
registerAdapter(Fetcher, IClient, IWebWorld)

# may come in handy to add a body to requests
#from twisted.web.iweb import IBodyProducer
#class StringProducer(object):
   #implements(IBodyProducer)

   #def __init__(self, body):
       #self.body = body
       #self.length = len(body)

   #def startProducing(self, consumer):
       #consumer.write(self.body)
       #return succeed(None)

   #def pauseProducing(self):
       #pass

   #def stopProducing(self):
       #pass
