'Utility functions'
import json

from aiohttp import web

def json_response(data, **kwargs):
    '''return a JSON response'''
    kwargs.setdefault('content_type', 'application/json')
    return web.Response(text=json.dumps(data), **kwargs)
