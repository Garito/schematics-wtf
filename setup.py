#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='schematics-wtf',
    version='0.1.2-alpha',
    license='BSD',
    description='Schematics Model to WTForm converter',
    url='http://github.com/Garito/schematics-wtf',
    packages=['schematics_wtf'],
    install_requires = [
        'schematics>=1.0-0',
        'wtforms'
    ],
    dependency_links = [
        'https://github.com/j2labs/schematics/tarball/master#egg=schematics-1.0-0'
    ],
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
