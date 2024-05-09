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

``duplicate-url-discarder`` contains a Scrapy fingerprinter that uses
customizable URL processors to canonicalize URLs before fingerprinting.

Quick Start
***********

Installation
============

.. code-block::

    pip install duplicate-url-discarder

Requires **Python 3.8+**.

Using
=====

Enable the Scrapy fingerprinter:

.. code-block:: python

    REQUEST_FINGERPRINTER_CLASS = "duplicate_url_discarder.Fingerprinter"

It will make fingerprints using canonical forms of the request URLs. Requests
with the ``"dud"`` meta value set to ``False`` are processed using a fallback
fingerprinter (which is the default Scrapy one unless another one is configured
in the ``DUD_FALLBACK_REQUEST_FINGERPRINTER_CLASS`` setting).

URL Processors
==============

``duplicate-url-discarder`` utilizes *URL processors* to make canonical
versions of URLs. The processors are configured with *URL rules*. Each URL rule
specifies an URL pattern for which the processor applies, and specific
processor arguments to use.

The following URL processors are currently available:

* ``queryRemoval``: removes query string parameters *(i.e. key=value)*, wherein
  the keys are specified in the arguments. If a given key appears multiple times
  with different values in the URL, all of them are removed.

URL Rules
=========

A URL rule is a dictionary specifying the ``url-matcher`` URL pattern(s), the
URL processor name, the URL processor args and the order that is used to sort
the rules. They are loaded from JSON files that contain arrays of serialized
rules:

.. code-block:: json

    [
      {
        "args": [
          "foo",
          "bar",
        ],
        "order": 100,
        "processor": "queryRemoval",
        "urlPattern": {
          "include": [
            "foo.example"
          ]
        }
      },
      {
        "args": [
          "PHPSESSIONID"
        ],
        "order": 100,
        "processor": "queryRemoval",
        "urlPattern": {
          "include": []
        }
      }
    ]

All non-universal rules (ones that have non-empty include pattern) that match
a request URL are applied according to their order field. If there are no
non-universal rules that match the URL, the universal ones are applied.

Configuration
=============

``duplicate-url-discarder`` uses the following Scrapy settings:

``DUD_LOAD_RULE_PATHS``: it should be a list of file paths (``str`` or
``pathlib.Path``) pointing to JSON files with the URL rules to apply:

.. code-block:: python

    DUD_LOAD_RULE_PATHS = [
        "/home/user/project/custom_rules1.json",
    ]

The default value of this setting is empty.
