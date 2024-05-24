import json
from pathlib import Path
from typing import Any, Dict

import pytest
from scrapy import Request, Spider
from scrapy.dupefilters import BaseDupeFilter, RFPDupeFilter
from scrapy.utils.test import get_crawler

from duplicate_url_discarder import Fingerprinter


async def get_fingerprinter(settings_dict: Dict[str, Any]) -> Fingerprinter:
    crawler = get_crawler(Spider, settings_dict)
    fp = Fingerprinter.from_crawler(crawler)
    await fp.spider_opened(crawler.spider)
    return fp


def get_df(fingerprinter: Fingerprinter) -> BaseDupeFilter:
    return RFPDupeFilter.from_settings(
        fingerprinter.crawler.settings, fingerprinter=fingerprinter
    )


@pytest.mark.asyncio
async def test_fingerprinter(tmp_path):
    rules_path = Path(tmp_path) / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "args": ["bbn", "node"],
                    "order": 100,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": ["bar.example"]},
                },
                {
                    "args": ["PHPSESSIONID"],
                    "order": 1,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": []},
                },
            ]
        )
    )
    fingerprinter = await get_fingerprinter({"DUD_LOAD_RULE_PATHS": [str(rules_path)]})
    assert len(fingerprinter.url_canonicalizer.processors) == 2

    def get_stat(stat: str) -> Any:
        return fingerprinter.crawler.stats.get_value(
            f"duplicate_url_discarder/request/{stat}"
        )

    df = get_df(fingerprinter)
    assert not df.request_seen(Request(url="http://foo.example/?foo=bar"))
    assert not df.request_seen(Request(url="http://foo.example/?foo=baz"))
    # exact same URL as before
    assert df.request_seen(Request(url="http://foo.example/?foo=baz"))
    # removing an argument (via a universal rule)
    assert df.request_seen(
        Request(url="http://foo.example/?PHPSESSIONID=11111&foo=baz")
    )
    assert get_stat("url_modified") == 1
    # a rule for a different domain isn't applied
    assert not df.request_seen(Request(url="http://foo.example/?bbn=11111&foo=baz"))
    assert get_stat("url_modified") == 1

    assert not df.request_seen(Request(url="http://bar.example/?foo=baz"))
    # a universal rule isn't applied
    assert not df.request_seen(
        Request(url="http://bar.example/?PHPSESSIONID=11111&foo=baz")
    )
    assert get_stat("url_modified") == 1
    # removing an argument (via a domain rule)
    assert df.request_seen(Request(url="http://bar.example/?bbn=11111&foo=baz"))
    assert get_stat("url_modified") == 2

    # skipping via dud=False, only if the exact URL wasn't seen before
    assert not df.request_seen(
        Request(url="http://bar.example/?bbn=11112&foo=baz", meta={"dud": False})
    )
    assert get_stat("url_modified") == 2

    # the method and body values are considered in the fingerprint
    assert not df.request_seen(
        Request(url="http://foo.example/?foo=bar", method="POST")
    )
    assert get_stat("url_modified") == 2
    assert not df.request_seen(
        Request(url="http://foo.example/?foo=bar", method="POST", body="body")
    )
    assert get_stat("url_modified") == 2
    assert df.request_seen(
        Request(
            url="http://foo.example/?PHPSESSIONID=11111&foo=bar",
            method="POST",
            body="body",
        )
    )
    assert get_stat("url_modified") == 3
