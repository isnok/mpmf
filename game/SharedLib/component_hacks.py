from twisted.python.components import registerAdapter

def registerGlobal(instance, interface):
    def getInstance(ignored):
        return instance
    registerAdapter(getInstance, str, interface)
    registerAdapter(getInstance, int, interface)
    registerAdapter(getInstance, None, interface)

def registerIDs(factory, cache, interface):
    def getInstance(ID):
        if ID in cache:
            return cache[ID]
        return cache.setdefault(ID, factory(ID))
    registerAdapter(getInstance, str, interface)
    registerAdapter(getInstance, int, interface)
    registerAdapter(getInstance, None, interface)


from twisted.python import log as twisted_log

class ConfiguredObject(object):

    """ Configure objects:
            - store configuration object
            - equip them with convenient logging functions

    """

    def __init__(self, config):
        self.config = config
        self.configure(config)

    def configure(self, config):
        """ The replacement __init__ for a ConfiguredObject. """

    def log(self, msg, context=None, log=twisted_log.msg):
        if context is None:
            log('%s - %s' % (self, msg))
        else:
            log('%s - %s: %s' % (self, context, msg))
        return msg

    def err(self, msg, context=None):
        return self.log(msg, context, log=twisted_log.err)



from SharedLib.Interfaces import IMainSetup

class NamedObject(ConfiguredObject):

    """ An objects name is a machine-friendly string. """

    def __init__(self, name):
        cfg = IMainSetup(42)
        ConfiguredObject.__init__(self, cfg)
        if not hasattr(self, 'name') or self.name is None: # might be set via configure
            self.name = name
        self.log("Sucessfully instanciated.")

    def __str__(self):
        return "<%s named %s>" % (self.__class__.__name__, self.name)


from twisted.python.components import Componentized

class NamedComponentized(NamedObject, Componentized):

    def __init__(self, name):
        Componentized.__init__(self)
        NamedObject.__init__(self, name)

from twisted.python.components import Adapter

class NamedAdapter(Adapter, NamedObject):

    def __init__(self, original):
        Adapter.__init__(self, original)
        self.name = original.name
        NamedObject.__init__(self, original.name)
