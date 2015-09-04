#!/usr/bin/env python

import sys

from setuptools import setup

install_requires = []
if sys.version_info < (3, 4):
    install_requires.append('enum34')

setup(
    name="ReParser",
    version="1.4.3",
    description="Simple regex-based lexer/parser for inline markup",
    author="Michal Krenek (Mikos)",
    author_email="m.krenek@gmail.com",
    url="https://github.com/xmikos/reparser",
    license="MIT",
    py_modules=["reparser"],
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup"
    ]
)
