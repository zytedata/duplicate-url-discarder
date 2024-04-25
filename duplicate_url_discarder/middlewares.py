from __future__ import annotations

import os
from typing import TYPE_CHECKING, List, Set, Union

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.http import Response
from scrapy.utils.request import RequestFingerprinterProtocol

from .url_canonicalizer import UrlCanonicalizer

if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self


class DuplicateUrlDiscarderDownloaderMiddleware:
    def __init__(self, crawler: Crawler):
        self.crawler: Crawler = crawler
        rule_paths: List[Union[str, os.PathLike]] = self.crawler.settings.getlist(
            "DUD_LOAD_RULE_PATHS"
        )
        if not rule_paths:
            raise NotConfigured("No DUD_LOAD_RULE_PATHS set")
        self.url_canonicalizer = UrlCanonicalizer(rule_paths)
        assert crawler.request_fingerprinter
        self._fingerprinter: RequestFingerprinterProtocol = (
            crawler.request_fingerprinter
        )
        self._fingerprints: Set[bytes] = set()

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(crawler)

    def process_request(self, request: Request) -> Union[Request, Response, None]:
        if request.dont_filter:
            return None
        if not request.meta.get("dud", True):
            self.crawler.stats.inc_value("duplicate_url_discarder/request/skipped")
            return None
        canonical_url = self.url_canonicalizer.process_url(request.url)
        fp = self._fingerprinter.fingerprint(request.replace(url=canonical_url))
        if fp in self._fingerprints:
            self.crawler.stats.inc_value("duplicate_url_discarder/request/discarded")
            raise IgnoreRequest(
                f"Duplicate URL discarded: {request.url} (canonical URL: {canonical_url})"
            )
        self._fingerprints.add(fp)
        self.crawler.stats.inc_value("duplicate_url_discarder/request/allowed")
        return None
