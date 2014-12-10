#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='schematics-wtf',
    version='0.1.2-alpha',
    license='BSD',
    description='Schematics Model to WTForm converter',
    url='http://github.com/Garito/schematics-wtf',
    download_url='https://github.com/Garito/schematics-wtf/tarball/0.1.2-alpha',
    packages=['schematics_wtf'],
    author = 'Garito',
    author_email = 'garito@gmail.com',
    install_requires = [
        'schematics>=1.0-0',
        'wtforms'
    ],
    dependency_links = [
        'https://github.com/schematics/schematics/tarball/master#egg=schematics-1.0-0'
    ],
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
)
