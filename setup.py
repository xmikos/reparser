#!/usr/bin/env python

from setuptools import setup

setup(
    name="ReParser",
    version="1.4.2",
    description="Simple regex-based lexer/parser for inline markup",
    author="Michal Krenek (Mikos)",
    author_email="m.krenek@gmail.com",
    url="https://github.com/xmikos/reparser",
    license="MIT",
    py_modules=["reparser"],
    install_requires=[
        "enum34"  # Only needed for backward compatibility with Python < 3.4
    ],
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
