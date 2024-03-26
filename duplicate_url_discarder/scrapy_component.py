import os
from typing import List, Union

from scrapy import Request
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured

from duplicate_url_discarder.processor import Processor


class Component:  # TODO
    def __init__(self, crawler: Crawler):
        self.crawler: Crawler = crawler
        policy_path: List[Union[str, os.PathLike]] = self.crawler.settings.getlist(
            "DUD_LOAD_POLICY_PATH"
        )
        if not policy_path:
            raise NotConfigured("No DUD_LOAD_POLICY_PATH set")
        self.processor = Processor(policy_path)

    def process_request(self, request: Request):
        url = self.processor.process_url(request.url)
        if url == request.url:
            return request
        return request.replace(url=url)
