=======================
duplicate-url-discarder
=======================

.. image:: https://img.shields.io/pypi/v/duplicate-url-discarder.svg
   :target: https://pypi.python.org/pypi/duplicate-url-discarder
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/duplicate-url-discarder.svg
   :target: https://pypi.python.org/pypi/duplicate-url-discarder
   :alt: Supported Python Versions

.. image:: https://github.com/scrapinghub/duplicate-url-discarder/workflows/tox/badge.svg
   :target: https://github.com/scrapinghub/duplicate-url-discarder/actions
   :alt: Build Status

.. image:: https://codecov.io/github/scrapinghub/duplicate-url-discarder/coverage.svg?branch=master
   :target: https://codecov.io/gh/scrapinghub/duplicate-url-discarder
   :alt: Coverage report

.. image:: https://readthedocs.org/projects/duplicate-url-discarder/badge/?version=stable
   :target: https://duplicate-url-discarder.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status

``duplicate-url-discarder`` contains Scrapy components that allow discarding
requests with duplicate URLs, using customizable policies to configure which
URLs are considered duplicate.

Quick Start
***********

Installation
============

.. code-block::

    pip install duplicate-url-discarder

Requires **Python 3.8+**.

Using
=====

Enable the Scrapy component:

.. code-block:: python

    ...

It will replace the request URLs with their canonical forms, using configured
policies.

Policies
========

``duplicate-url-discarder`` utilizes *policies* to make canonical versions of
URLs. The policies are configured with *URL rules*. Each URL rule specifies
an URL pattern that a policy applies to and specific policy arguments to use.

The following policies are currently available:

* ``queryRemoval``: removes query string parameters, their names are specified
  in the arguments.

Configuration
=============

``duplicate-url-discarder`` uses the following Scrapy settings:

``DUD_LOAD_POLICY_PATH``: it should be a list of file paths (``str`` or
``pathlib.Path``) pointing to files with the URL rules to apply. The default
value of this setting points to the default rules file.
