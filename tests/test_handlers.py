import pytest

import json
import mockaioredis

from orchestrator import handlers, version
from orchestrator.app import generate_app

async def init_redis(app):
    engine = await mockaioredis.create_pool(
        'fake address',
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
    client = await test_client(create_app)
    resp = await client.post('/api/v1.0/downloaded', data=b'{"foo": "bar"}')
    assert 204 == resp.status


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
