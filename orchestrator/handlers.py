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
    if 'job_id' not in data:
        return json_response({'error': 'invalid request'}, status=400)
    async with request.app['redis_pool'].get() as redis:
        try:
            job = Job(redis, data['job_id'])
            await job.fetch()
        except ValueError as e:
            return json_response(
                {'error': str(e)},
                status=404)

        job.state = 'queued'
        job.status = 'Input downloaded, awaiting processing.'
        await job.commit()
        await redis.lpush('aso:queued', job.job_id)
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
    return json_response(job.to_dict(extra_info=True), status=201)
