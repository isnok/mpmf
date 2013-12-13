from twisted.python import log
from twisted.web.resource import Resource

import json

class JsonResource(Resource):
    isLeaf = True

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def render_GET(self, request, success=True):
        request.setHeader("content-type", "application/json")
        success = True
        return json.dumps({
            'success': success,
            'res': self.name,
            'data': self.data
        })
