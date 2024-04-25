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

``duplicate-url-discarder`` contains a Scrapy middleware that allows discarding
requests with duplicate URLs, using customizable URL processors to configure
which URLs are considered duplicate.

Quick Start
***********

Installation
============

.. code-block::

    pip install duplicate-url-discarder

Requires **Python 3.8+**.

Using
=====

Enable the Scrapy middleware:

.. code-block:: python

    DOWNLOLADER_MIDDLEWARES = {
        "duplicate_url_discarder.DuplicateUrlDiscarderDownloaderMiddleware": 540,
    }

It will process requests, making canonical forms of their URLs and discarding
requests with the same canonical URL form as earlier ones. Only requests with
the ``"dud"`` meta value set to ``True`` are processed in this way.

URL Processors
==============

``duplicate-url-discarder`` utilizes *URL processors* to make canonical
versions of URLs. The processors are configured with *URL rules*. Each URL rule
specifies an URL pattern that a processor applies to and specific processor
arguments to use.

The following URL processors are currently available:

* ``queryRemoval``: removes query string parameters *(i.e. key=value)*, wherein
  the keys are specified in the arguments. If a given key appears multiple times
  with different values in the URL, all of them are removed.

Configuration
=============

``duplicate-url-discarder`` uses the following Scrapy settings:

``DUD_LOAD_RULE_PATHS``: it should be a list of file paths (``str`` or
``pathlib.Path``) pointing to files with the URL rules to apply. The default
value of this setting points to the default rules file.
