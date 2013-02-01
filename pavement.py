# Copyright (c) 2010-2013 Adi Roiban.
# See LICENSE for details.
"""
Build script for chevah-compat.
"""
from __future__ import with_statement
import sys

# This value is pavers by bash. Use a strict format.
BRINK_VERSION = '0.9.0'

EXTRA_PACKAGES = [
    # FIXME:1022:
    # For new we need to update it by hand.
    'chevah-compat==0.5.0-adi3',
    'chevah-empirical==0.5.0-adi6',
    ]

from brink.pavement_commons import (
    _p,
    buildbot_list,
    buildbot_try,
    default,
    github,
    harness,
    help,
    lint,
    pave,
    SETUP,
    test,
    test_remote,
    test_normal,
    test_super,
    )
from paver.easy import task

# Make pylint shut up.
buildbot_list
buildbot_try
default
github,
harness
help
lint
test
test_remote
test_normal
test_super

SETUP['product']['name'] = 'chevah-utils'
SETUP['folders']['source'] = u'chevah/utils'
SETUP['repository']['name'] = u'utils'
SETUP['pocket-lint']['include_files'] = ['pavement.py']
SETUP['pocket-lint']['include_folders'] = ['chevah/utils']
SETUP['pocket-lint']['exclude_files'] = []
SETUP['test']['package'] = 'chevah.utils.tests'
SETUP['test']['elevated'] = 'elevated'


@task
def deps():
    """
    Copy external dependencies.
    """
    print('Installing dependencies to %s...' % (pave.path.build))
    pave.installRunDependencies(extra_packages=EXTRA_PACKAGES)
    pave.installBuildDependencies()


@task
def build():
    """
    Copy new source code to build folder.
    """
    build_target = _p([pave.path.build, 'setup-build'])
    sys.argv = ['setup.py', 'build', '--build-base', build_target]
    print "Building in " + build_target
    import setup
    setup.distribution.run_command('install')
