#!/usr/bin/env python
#
# setup.py - setuptools configuration for installing the fslpy package.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import os.path as op

from setuptools import setup
from setuptools import find_packages


# The directory in whihc this setup.py file is contained.
basedir = op.dirname(__file__)


# Figure out the current fslpy version, as defined in fsl/version.py. We
# don't want to import the fsl package,  as this may cause build problems.
# So we manually parse the contents of fsl/version.py to extract the
# version number.
version = {}
with open(op.join(basedir, "fsl", "version.py")) as f:
    exec(f.read(), version)

install_requires = open(op.join(basedir, 'requirements.txt'), 'rt').readlines()

dependency_links = [i for i in install_requires if     i.startswith('git')]
install_requires = [i for i in install_requires if not i.startswith('git')]

setup(

    name='fslpy',

    version=version['__version__'],

    description='FSL Python library',

    url='https://git.fmrib.ox.ac.uk/paulmc/fslpy',

    author='Paul McCarthy',

    author_email='pauldmccarthy@gmail.com',

    license='FMRIB',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Free for non-commercial use',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    packages=find_packages(exclude=('doc')),

    install_requires=install_requires,
    dependency_links=dependency_links,

    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-runner'],
    test_suite='tests',
)
