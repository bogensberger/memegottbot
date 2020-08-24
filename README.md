Install Packages
================

Setup a virtualenv:

    python3 -m venv .venv
    .venv/bin/python -m pip install -U pip setuptools
    .venv/bin/python -m pip install -r requirements.txt

To upgrade dependencies, just install requirements again:

    .venv/bin/python -m pip install -r requirements.txt

Run Script
==========

To Start the listening Bot, run::

    .venv/bin/python3 bot.py --start <api-token>
