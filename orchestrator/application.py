'Main orchestrator logic'

import aioredis
import logging

from aiohttp import web, log
from aiohttp_route_decorator import RouteCollector, Route
from envparse import Env

from . import handlers
from .version import git_version

def generate_routes(app):
    routes = RouteCollector(prefix="/api/v1.0", routes=[
        Route('/version', handlers.version, method='GET'),
        Route('/downloaded', handlers.downloaded, method='POST'),
        Route('/session', handlers.sessionNew, method='POST'),
    ])

    routes.add_to_router(app.router)


# Manage redis connection
async def init_redis(app):
    env = app['config']
    engine = await aioredis.create_pool(
        (env('ASO_REDIS_HOST'), env('ASO_REDIS_PORT')),
        db=env('ASO_REDIS_DB'),
        loop=app.loop
    )
    app['redis_pool'] = engine


async def close_redis(app):
    'Shut down redis connection on exit'
    log.server_logger.info('Closing redis connection')
    app['redis_pool'].close()
    await app['redis_pool'].wait_closed()


def generate_app(redis_init=init_redis, git_version_getter=git_version,
                 loop=None):

    # Configuration variables schema
    env = Env(
        ASO_REDIS_HOST=dict(default='localhost'),
        ASO_REDIS_PORT=dict(cast=int, default=6379),
        ASO_REDIS_DB=dict(cast=int, default=0),
        ASO_ID_PREFIX=dict(default='bacteria'),
        ASO_DEBUG=dict(cast=bool, default=False))

    if env('ASO_DEBUG'):
        logging.basicConfig(level='DEBUG')

    app = web.Application(loop=loop)
    app['config'] = env

    app.on_startup.append(redis_init)
    app.on_startup.append(git_version_getter)
    app.on_cleanup.append(close_redis)

    generate_routes(app)
    return app
