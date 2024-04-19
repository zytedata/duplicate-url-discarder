import hashlib
import os
from typing import List, Set, Union

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.http import Response

from .url_canonicalizer import UrlCanonicalizer


class DuplicateUrlDiscarderDownloaderMiddleware:
    def __init__(self, crawler: Crawler):
        self.crawler: Crawler = crawler
        rule_paths: List[Union[str, os.PathLike]] = self.crawler.settings.getlist(
            "DUD_LOAD_RULE_PATHS"
        )
        if not rule_paths:
            raise NotConfigured("No DUD_LOAD_RULE_PATHS set")
        self.url_canonicalizer = UrlCanonicalizer(rule_paths)
        self._fingerprints: Set[str] = set()

    @staticmethod
    def _url_fingerprint(url: str) -> str:
        return hashlib.sha1(url.encode()).hexdigest()

    def process_request(self, request: Request) -> Union[Request, Response, None]:
        if not request.meta.get("dud", False):
            self.crawler.stats.inc_value("duplicate_url_discarder/request/skipped")
            return None
        canonical_url = self.url_canonicalizer.process_url(request.url)
        fp = self._url_fingerprint(canonical_url)
        if fp in self._fingerprints:
            self.crawler.stats.inc_value("duplicate_url_discarder/request/discarded")
            raise IgnoreRequest(f"Duplicate URL discarded: {canonical_url}")
        self._fingerprints.add(fp)
        self.crawler.stats.inc_value("duplicate_url_discarder/request/allowed")
        return None
