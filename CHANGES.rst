Changes
=======

0.3.0 (2024-12-30)
------------------

* Added Python 3.13 support, dropped Python 3.8 support.

* Improved Scrapy 2.12 support (deprecations).

* Fixed the duplicate logging of dropped items.

* The message logged when using the default rules is no longer a warning.

* Improved the docs:

    * Documented how to deploy custom rule files.

    * Documented missing processors.

0.2.0 (2024-07-23)
------------------

* New URL Processors:

    * ``SubpathRemovalProcessor`` removes the subpaths of a URL based on its
      integer positions.
    * ``NormalizerProcessor`` removes trailing ``/`` and ``www.`` prefixes 
      which also includes numbers like ``www2.``

* New Item Pipeline ``DuplicateUrlDiscarderPipeline`` to remove duplicate items
  based on some attributes.

0.1.0 (2024-07-08)
------------------

* Initial version.
