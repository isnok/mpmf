
import requests
import time

from tools import output

class Connection():
    
    def __init__(self, queue, commands, host, port, path='/', debug=False, username=None, password=None,):
        self.connected = False
        self.queue = queue
        self.commands = commands
        self.debug = debug
        self.host = host
        self.port = port
        self.path = path.lstrip('/')
        self.url = 'http://%s:%s/%s' % (self.host, self.port, self.path)
        
        self.auth = None
        if username is not None: 
            self.auth = requests.auth.HTTPBasicAuth(username, password)
         
        output('Connecting to url: %s' % self.url, 'info', source='Connection().__init__()')
        
        self.run()

    def get_update(self, path=None):

        url = self.build_url(path)
        
        command = None
        while not self.commands.empty():
            command = self.commands.get()

        try:
            if command is not None:
                response = requests.get(url, params=command['data'], allow_redirects=True, timeout=0.5, auth=self.auth)
            else:
                response = requests.get(url, allow_redirects=True, timeout=0.5, auth=self.auth)
        except:
            output('Connecting to url: %s' % self.url, 'warning', source='Connection().get_update()')
        else:
            self.queue.put(response.json())
    
    def build_url(self, path=None):
        if path is None:
            return self.url
        return "%s/%s" % (self.url.rstrip('/'), path.lstrip('/'))
    
    def run(self):
        self.get_update('map')
        self.get_update('walk')
        while True:
            self.get_update('enemies')
            self.get_update('towers')
            self.get_update('players')
            time.sleep(0.1)

