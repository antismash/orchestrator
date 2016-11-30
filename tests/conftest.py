import subprocess

import pytest


@pytest.fixture
def git_version():
    args = ['git', 'rev-parse', '--short', 'HEAD']
    prog = subprocess.Popen(args, stdout=subprocess.PIPE)
    output = prog.stdout.readline()
    git_ver = output.decode('utf-8').strip()
    return git_ver
