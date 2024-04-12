import os
from typing import List, Set, Union

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.http import Response

from duplicate_url_discarder.processor import Processor


class DuplicateUrlDiscarderDownloaderMiddleware:
    def __init__(self, crawler: Crawler):
        self.crawler: Crawler = crawler
        policy_path: List[Union[str, os.PathLike]] = self.crawler.settings.getlist(
            "DUD_LOAD_POLICY_PATH"
        )
        if not policy_path:
            raise NotConfigured("No DUD_LOAD_POLICY_PATH set")
        self.processor = Processor(policy_path)
        self.canonical_urls: Set[str] = set()

    def process_request(self, request: Request) -> Union[Request, Response, None]:
        if not request.meta.get("dud", False):
            return None
        canonical_url = self.processor.process_url(request.url)
        if canonical_url in self.canonical_urls:
            raise IgnoreRequest(f"Duplicate URL discarded: {canonical_url}")
        self.canonical_urls.add(canonical_url)
        return None
