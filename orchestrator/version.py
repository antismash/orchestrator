import asyncio
import asyncio.subprocess

__version__ = '0.1.0'


async def git_version(app):
    '''get the git version if available'''
    args = ['git', 'rev-parse', '--short', 'HEAD']
    git_ver = await asyncio.create_subprocess_exec(*args, loop=app.loop, stdout=asyncio.subprocess.PIPE)
    output = await git_ver.stdout.readline()
    line = output.decode('utf-8').strip()
    await git_ver.wait()
    app['git_version'] = line
