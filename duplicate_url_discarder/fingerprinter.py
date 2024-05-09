from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, List, Union

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.settings.default_settings import (
    REQUEST_FINGERPRINTER_CLASS as ScrapyRequestFingerprinter,
)
from scrapy.utils.misc import create_instance, load_object
from scrapy.utils.request import RequestFingerprinterProtocol

from .url_canonicalizer import UrlCanonicalizer

if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self

logger = logging.getLogger(__name__)


class Fingerprinter:
    def __init__(self, crawler: Crawler):
        self.crawler: Crawler = crawler
        rule_paths: List[Union[str, os.PathLike]] = self.crawler.settings.getlist(
            "DUD_LOAD_RULE_PATHS"
        )
        if not rule_paths:
            logger.warning("DUD_LOAD_RULE_PATHS is not set or is empty.")
        self._fallback_request_fingerprinter: RequestFingerprinterProtocol = (
            create_instance(
                load_object(
                    crawler.settings.get(
                        "DUD_FALLBACK_REQUEST_FINGERPRINTER_CLASS",
                        ScrapyRequestFingerprinter,
                    )
                ),
                settings=crawler.settings,
                crawler=crawler,
            )
        )
        self.url_canonicalizer = UrlCanonicalizer(rule_paths)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        return cls(crawler)

    def fingerprint(self, request: Request) -> bytes:
        if not request.meta.get("dud", True):
            self.crawler.stats.inc_value("duplicate_url_discarder/request/skipped")
            return self._fallback_request_fingerprinter.fingerprint(request)
        canonical_url = self.url_canonicalizer.process_url(request.url)
        self.crawler.stats.inc_value("duplicate_url_discarder/request/processed")
        return self._fallback_request_fingerprinter.fingerprint(
            request.replace(url=canonical_url)
        )
