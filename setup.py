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

setup(

    name='fslpy',

    version=version['__version__'],

    description='Front end to FSL tools',

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

    install_requires=[
        'pyopengl>=3.1.0',
        'pyparsing>=2.0.3',
        'numpy>=1.8.1',
        'scipy>=0.14.0',
        'matplotlib>=1.3.1',
        'nibabel>=1.3.0',
        'Pillow>=2.5.3'],

    package_data={
        'fsl' : [
            'fsleyes/splash.png',
            'fsleyes/icons/*.png',
            'fsleyes/gl/gl14/*prog',
            'fsleyes/gl/gl21/*glsl',
            'fsleyes/colourmaps/*cmap',
            'fsleyes/luts/*lut',
            'fsleyes/colourmaps/README',
            'fsleyes/colourmaps/order.txt',
            'fsleyes/luts/order.txt',
        ]
    },

    entry_points={'console_scripts' : ['fslpy = fsl:main']}
)
