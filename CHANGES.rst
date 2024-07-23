Changes
=======

0.2.0 (YYYY-MM-DD)
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
