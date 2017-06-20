import os
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

short_description = "Orchestrator for the antiSMASH microservice architecture"
long_description = short_description
if os.path.exists('README.rst'):
    long_description = open('README.rst').read()

install_requires = [
    'aiodns',
    'aiohttp',
    'aiohttp-route-decorator',
    'aioredis',
    'cchardet',
    'envparse',
    'gunicorn',
]


tests_require = [
    'pytest',
    'coverage',
    'pytest-cov',
    'mockredispy-kblin>=2.3.9.1',
    'mockaioredis',
]


def read_version():
    for line in open(os.path.join('orchestrator', 'version.py'), 'r'):
        if line.startswith('__version__'):
            return line.split('=')[-1].strip().strip("'")


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='antismash-orchestrator',
    version=read_version(),
    author='Kai Blin',
    author_email='kblin@biosustain.dtu.dk',
    description=short_description,
    long_description=long_description,
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    packages=['orchestrator'],
    url='https://github.com/antismash/orchestrator/',
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
    ],
    extras_require={
        'testing': tests_require,
    },
)
