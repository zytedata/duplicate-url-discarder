__version__ = "0.1.0"

from ._rule import UrlRule, load_rules, save_rules
from .middlewares import DuplicateUrlDiscarderDownloaderMiddleware
from .url_canonicalizer import UrlCanonicalizer
