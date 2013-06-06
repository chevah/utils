# Copyright (c) 2010-2013 Adi Roiban.
# See LICENSE for details.
"""
Build script for chevah-compat.
"""
from __future__ import with_statement
import sys

# This value is pavers by bash. Use a strict format.
BRINK_VERSION = '0.22.0'
PYTHON_VERSION = '2.7'

RUN_PACKAGES = [
    # FIXME:1022:
    # For new we need to update it by hand.
    'chevah-compat==0.8.2',
    'chevah-empirical==0.14.0',
    'zope.interface==3.8.0',
    'twisted==12.1.0-chevah3',
    'pyasn1',
    'jinja2',
    ]

BUILD_PACKAGES = [
    'sphinx==1.1.3-chevah1',
    'repoze.sphinx.autointerface==0.7.1-chevah2',
    # Docutils is required for RST parsing and for Sphinx.
    'docutils>=0.9.1-chevah2',

    # Buildbot is used for try scheduler
    'buildbot',

    # For PQM
    'chevah-github-hooks-server==0.1.6',
    'smmap==0.8.2',
    'async==0.6.1',
    'gitdb==0.5.4',
    'gitpython==0.3.2.RC1',
    'pygithub==1.10.0',
    ]

TEST_PACKAGES = [
    'pyflakes>=0.5.0-chevah2',
    'closure_linter==2.3.9',
    'pocketlint==0.5.31-chevah7',
    'pocketlint-jshint',

    # Never version of nose, hangs on closing some tests
    # due to some thread handling.
    'nose==1.1.2-chevah1',
    'mock',

    # Test SFTP service using a 3rd party client.
    'paramiko',

    # Required for some unicode handling.
    'unidecode',

    'bunch',
    ]

from brink.pavement_commons import (
    buildbot_list,
    buildbot_try,
    default,
    github,
    harness,
    help,
    lint,
    merge_init,
    merge_commit,
    pave,
    pqm,
    SETUP,
    test,
    test_remote,
    test_normal,
    test_super,
    )
from paver.easy import needs, task

# Make pylint shut up.
buildbot_list
buildbot_try
default
github,
harness
help
lint
merge_init
merge_commit
pqm
test
test_remote
test_normal
test_super

SETUP['product']['name'] = 'chevah-utils'
SETUP['folders']['source'] = u'chevah/utils'
SETUP['repository']['name'] = u'utils'
SETUP['github']['repo'] = u'chevah/utils'
SETUP['pocket-lint']['include_files'] = ['pavement.py']
SETUP['pocket-lint']['include_folders'] = ['chevah/utils']
SETUP['pocket-lint']['exclude_files'] = []
SETUP['test']['package'] = 'chevah.utils.tests'
SETUP['test']['elevated'] = 'elevated'


@task
def deps():
    """
    Install dependencies for testing environment.
    """
    print('Installing dependencies to %s...' % (pave.path.build))
    pave.pip(
        command='install',
        arguments=RUN_PACKAGES,
        )
    pave.pip(
        command='install',
        arguments=TEST_PACKAGES,
        )


@task
@needs('deps')
def deps_build():
    """
    Install dependencies for build environment.
    """
    print('Installing build dependencies to %s...' % (pave.path.build))
    pave.pip(
        command='install',
        arguments=BUILD_PACKAGES,
        )


@task
def build():
    """
    Copy new source code to build folder.
    """
    # Clean previous files.
    pave.fs.deleteFolder([
        pave.path.build,
        pave.getPythonLibPath(python_version=PYTHON_VERSION),
        'chevah',
        'utils',
        ])
    pave.fs.deleteFolder([pave.path.build, 'setup-build'])

    build_target = pave.fs.join([pave.path.build, 'setup-build'])
    sys.argv = ['setup.py', 'build', '--build-base', build_target]
    print "Building in " + build_target
    import setup
    setup.distribution.run_command('install')
