import pytest

from orchestrator import version


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
