import pytest

from orchestrator import version

from aiohttp.test_utils import loop_context


@pytest.yield_fixture
def loop():
    with loop_context() as loop:
        yield loop


@pytest.yield_fixture
def event_loop(loop):
    """
    This is needed for correct functioning of the test_client of aiohttp together with
    pytest.mark.asyncio pytest-asyncio decorator. For more info check the following link:
    https://github.com/KeepSafe/aiohttp/issues/939
    """
    loop._close = loop.close
    loop.close = lambda: None
    yield loop
    loop.close = loop._close

@pytest.mark.asyncio
async def test_git_version(git_version, event_loop):
    class FakeApp(dict):
        def __init__(self):
            self._dict = {}
            self.loop = None
        def __getitem__(self, key):
            return self._dict[key]
        def __setitem__(self, key, value):
            self._dict[key] = value

    app = FakeApp()

    app.loop = event_loop

    await version.git_version(app)
    assert app['git_version'] == git_version
