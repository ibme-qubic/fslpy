#!/usr/bin/env python
#
# test_run.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os.path as op
import            os
import            shutil
import            textwrap

# python 3
try:  from unittest import mock
# python 2
except ImportError: import mock

import six
import pytest

import fsl.utils.tempdir                  as tempdir
from   fsl.utils.platform import platform as fslplatform
import fsl.utils.run                      as run
import fsl.utils.fslsub                   as fslsub

from . import make_random_image, mockFSLDIR, CaptureStdout


def test_run():

    test_script = textwrap.dedent("""
    #!/bin/bash

    echo "standard output - arguments: $@"
    echo "standard error" >&2
    exit {}
    """).strip()

    with tempdir.tempdir():

        # return code == 0
        with open('script.sh', 'wt') as f:
            f.write(test_script.format(0))
        os.chmod('script.sh', 0o755)

        expstdout = "standard output - arguments: 1 2 3\n"
        expstderr = "standard error\n"

        # test:
        #   - single string
        #   - packed sequence
        #   - unpacked sequence
        assert run.run('./script.sh 1 2 3')             == expstdout
        assert run.run(('./script.sh', '1', '2', '3'))  == expstdout
        assert run.run(*('./script.sh', '1', '2', '3')) == expstdout

        # test stdout/stderr
        stdout, stderr = run.run('./script.sh 1 2 3', err=True)
        assert stdout == expstdout
        assert stderr == expstderr

        # test return code
        res = run.run('./script.sh 1 2 3', ret=True)
        stdout, ret = res
        assert stdout == expstdout
        assert ret == 0
        stdout, stderr, ret = run.run('./script.sh 1 2 3', err=True, ret=True)
        assert stdout == expstdout
        assert stderr == expstderr
        assert ret == 0

        # return code != 0
        with open('./script.sh', 'wt') as f:
            f.write(test_script.format(255))
        os.chmod('./script.sh', 0o755)

        with pytest.raises(RuntimeError):
            run.run('./script.sh 1 2 3')

        stdout, ret = run.run('./script.sh 1 2 3', ret=True)
        assert stdout == expstdout
        assert ret == 255


def test_run_tee():
    test_script = textwrap.dedent("""
    #!/bin/bash

    echo "standard output - arguments: $@"
    echo "standard error" >&2
    exit 0
    """).strip()

    with tempdir.tempdir():
        with open('script.sh', 'wt') as f:
            f.write(test_script)
        os.chmod('script.sh', 0o755)

        expstdout = "standard output - arguments: 1 2 3\n"
        expstderr = "standard error\n"

        capture = CaptureStdout()

        with capture:
            stdout = run.run('./script.sh 1 2 3', tee=True)

        assert stdout         == expstdout
        assert capture.stdout == expstdout

        with capture.reset():
            stdout, stderr = run.run('./script.sh 1 2 3', err=True, tee=True)

        assert stdout         == expstdout
        assert stderr         == expstderr
        assert capture.stdout == expstdout
        assert capture.stderr == expstderr

        with capture.reset():
            stdout, stderr, ret = run.run('./script.sh 1 2 3',
                                          err=True, ret=True, tee=True)

        assert ret            == 0
        assert stdout         == expstdout
        assert stderr         == expstderr
        assert capture.stdout == expstdout
        assert capture.stderr == expstderr

        with capture.reset():
            stdout, ret = run.run('./script.sh 1 2 3', ret=True, tee=True)

        assert ret            == 0
        assert stdout         == expstdout
        assert capture.stdout == expstdout


def test_dryrun():

    test_script = textwrap.dedent("""
    #!/bin/bash
    touch foo
    """).strip()

    with tempdir.tempdir():
        with open('./script.sh', 'wt') as f:
            f.write(test_script)
        os.chmod('./script.sh', 0o755)

        run.run('./script.sh')
        assert op.exists('foo')

        os.remove('foo')

        with run.dryrun():
            run.run('./script.sh')

        assert not op.exists('foo')


# test runfsl with/without $FSLDIR
def test_runfsl():

    test_script = textwrap.dedent("""
    #!/bin/bash
    echo {}
    exit 0
    """).strip()

    old_fsldir    = fslplatform.fsldir
    old_fsldevdir = fslplatform.fsldevdir


    try:
        with tempdir.tempdir():

            make_random_image('image.nii.gz')

            # no FSLDIR - should error
            fslplatform.fsldir    = None
            fslplatform.fsldevdir = None
            with pytest.raises(run.FSLNotPresent):
                run.runfsl('fslhd')

            # FSLDIR/bin exists - should be good
            fsldir = op.abspath('./fsl')
            fslhd  = op.join(fsldir, 'bin', 'fslhd')
            os.makedirs(op.join(fsldir, 'bin'))
            with open(fslhd, 'wt') as f:
                f.write(test_script.format('fsldir'))
            os.chmod(fslhd, 0o777)

            fslplatform.fsldir = fsldir
            assert run.runfsl('fslhd').strip() == 'fsldir'

            # FSLDEVDIR should take precedence
            fsldevdir = './fsldev'
            fslhd  = op.join(fsldevdir, 'bin', 'fslhd')
            shutil.copytree(fsldir, fsldevdir)
            with open(fslhd, 'wt') as f:
                f.write(test_script.format('fsldevdir'))

            fslplatform.fsldevdir = fsldevdir
            fslplatform.fsldir    = None
            assert run.runfsl('fslhd').strip() == 'fsldevdir'

            # FSL_PREFIX should override all
            override = './override'
            fslhd    = op.join(override, 'fslhd')
            os.makedirs(override)
            with open(fslhd, 'wt') as f:
                f.write(test_script.format('override'))
            os.chmod(fslhd, 0o777)


            fslplatform.fsldir    = None
            fslplatform.fsldevdir = None
            run.FSL_PREFIX = override
            assert run.runfsl('fslhd').strip() == 'override'

    finally:
        fslplatform.fsldir    = old_fsldir
        fslplatform.fsldevdir = old_fsldevdir
        run.FSL_PREFIX        = None


def mock_submit(cmd, **kwargs):
    if isinstance(cmd, six.string_types):
        name = cmd.split()[0]
    else:
        name = cmd[0]

    name = op.basename(name)

    jid = '12345'
    output = run.run(cmd)

    with open('{}.o{}'.format(name, jid), 'wt') as f:
        f.write(output)

    with open('{}.e{}'.format(name, jid), 'wt') as f:
        for k in sorted(kwargs.keys()):
            f.write('{}: {}\n'.format(k, kwargs[k]))

    return (jid,)


def test_run_submit():

    def mkexec(path, contents):
        with open(path, 'wt') as f:
            f.write(contents)
        os.chmod(path, 0o755)

    test_script = textwrap.dedent("""
    #!/usr/bin/env bash
    echo test_script running
    exit 0
    """).strip()

    with tempdir.tempdir(), \
         mockFSLDIR(), \
         mock.patch('fsl.utils.fslsub.submit', mock_submit):

        mkexec(op.expandvars('$FSLDIR/bin/fsltest'), test_script)

        jid = run.run('fsltest', submit=True)[0]

        assert jid == '12345'

        stdout, stderr = fslsub.output(jid)

        assert stdout == 'test_script running\n'
        assert stderr == ''

        kwargs = {'name' : 'abcde', 'ram' : '4GB'}

        jid = run.run('fsltest', submit=kwargs)[0]

        assert jid == '12345'

        stdout, stderr = fslsub.output(jid)

        experr = '\n'.join(['{}: {}'.format(k, kwargs[k])
                            for k in sorted(kwargs.keys())]) + '\n'

        assert stdout == 'test_script running\n'
        assert stderr == experr
