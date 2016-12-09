import pytest

import json
import mockaioredis

from orchestrator import handlers, version
from orchestrator.app import generate_app

async def init_redis(app):
    engine = await mockaioredis.create_pool(
        'fake address',
        encoding='utf-8',
        loop=app.loop
    )
    app['redis_pool'] = engine


async def fake_git_version(app):
    app['git_version'] = 'deadbeef'


def create_app(loop):
    app = generate_app(redis_init=init_redis, git_version_getter=fake_git_version,
                       loop=loop)
    return app


async def test_version(test_client):
    expected = {
        'api_version': version.__version__,
        'git_version': 'deadbeef',
    }

    client = await test_client(create_app)
    resp = await client.get('/api/v1.0/version')
    assert 200 == resp.status
    content = await resp.json()
    assert content == expected


async def test_downloaded(test_client):
    job = {
        'molecule_type': 'nucleotide',
        'genefinding': 'none',
        'state': 'downloading',
        'status': 'Downloading data from NCBI'
    }

    client = await test_client(create_app)
    async with client.app['redis_pool'].get() as redis:
        redis._redis.hmset('aso:job:bacterial-1234-5678', job)

    resp = await client.post('/api/v1.0/downloaded', data=b'{"foo": "bar"}')
    assert 400 == resp.status

    resp = await client.post('/api/v1.0/downloaded', data=b'{"job_id": "no-such-job"}')
    assert 404 == resp.status

    job['job_id'] = 'bacterial-1234-5678'
    resp = await client.post('/api/v1.0/downloaded', data=json.dumps(job).encode('utf-8'))
    assert 204 == resp.status

    async with client.app['redis_pool'].get() as redis:
        assert b'queued' == redis._redis.hget('aso:job:bacterial-1234-5678', 'state')


async def test_newSession(test_client):
    job = {
        'taxon': 'bacterial',
        'molecule_type': 'nucleotide',
        'genefinding': 'none',
        'smcogs': True
    }
    client = await test_client(create_app)
    resp = await client.post('/api/v1.0/session', data=json.dumps(job))
    assert 201 == resp.status
    data = await resp.json()

    expected = {
        'state': 'created',
        'status': 'Awaiting processing'
    }
    expected.update(job)
    assert 'job_id' in data
    assert data['job_id'].startswith('bacterial-')
    del data['job_id']
    assert expected == data
    resp.close()

    del job['taxon']
    resp = await client.post('/api/v1.0/session', data=json.dumps(job))
    assert 400 == resp.status
    data = await resp.json()
    assert {'error': 'invalid request'} == data
