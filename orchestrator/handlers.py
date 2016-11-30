'Handlers for the web service'
import uuid
import json
from aiohttp import web, log
from .version import (
    __version__,
    git_version,
)

from .utils import json_response
from .models import Job

async def version(request):
    res = {
        'api_version': __version__,
        'git_version': request.app['git_version']
    }

    return json_response(res)


async def downloaded(request):
    data = await request.json()
    log.server_logger.info(data)
    return web.Response(status=204)


async def sessionNew(request):
    '''Create a new session'''
    env = request.app['config']
    async with request.app['redis_pool'].get() as redis:
        data = await request.json()
        try:
            job = Job.from_dict(redis, data)
        except ValueError:
            return json_response({'error': 'invalid request'}, status=400)
        await job.commit()
        await redis.lpush('aso:created', job.job_id)
    return json_response(job.to_dict(), status=201)
