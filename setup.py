#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='schematics-wtf',
    version='0.1.5.6',
    license='BSD',
    description='Schematics Model to WTForm converter',
    url='http://github.com/Garito/schematics-wtf',
    download_url='http://pypi.python.org/pypi/dist/schematics-wtf-0.1.5.6.tar.gz',
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
