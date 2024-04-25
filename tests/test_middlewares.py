import json
import re
from pathlib import Path
from typing import Any, Dict

import pytest
from scrapy import Request, Spider
from scrapy.exceptions import IgnoreRequest, NotConfigured
from scrapy.utils.test import get_crawler

from duplicate_url_discarder import DuplicateUrlDiscarderDownloaderMiddleware


def get_mw(settings_dict: Dict[str, Any]) -> DuplicateUrlDiscarderDownloaderMiddleware:
    crawler = get_crawler(Spider, settings_dict)
    mw = DuplicateUrlDiscarderDownloaderMiddleware.from_crawler(crawler)
    return mw


@pytest.mark.parametrize(
    "settings", [{}, {"DUD_LOAD_RULE_PATHS": None}, {"DUD_LOAD_RULE_PATHS": []}]
)
def test_mw_empty_settings(settings):
    with pytest.raises(NotConfigured, match="No DUD_LOAD_RULE_PATHS set"):
        get_mw(settings)


def test_mw(tmp_path):
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
    mw = get_mw({"DUD_LOAD_RULE_PATHS": [str(rules_path)]})
    assert len(mw.url_canonicalizer.processors) == 2

    assert mw.process_request(Request(url="http://foo.example/?foo=bar")) is None
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/allowed") == 1
    assert mw.process_request(Request(url="http://foo.example/?foo=baz")) is None
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/allowed") == 2
    # exact same URL as before
    with pytest.raises(
        IgnoreRequest,
        match=re.escape(
            "Duplicate URL discarded: http://foo.example/?foo=baz (canonical URL: http://foo.example/?foo=baz)"
        ),
    ):
        mw.process_request(Request(url="http://foo.example/?foo=baz"))
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/discarded") == 1
    # removing an argument (via a universal rule)
    with pytest.raises(
        IgnoreRequest,
        match=re.escape(
            "Duplicate URL discarded: http://foo.example/?PHPSESSIONID=11111&foo=baz (canonical URL: http://foo.example/?foo=baz)"
        ),
    ):
        mw.process_request(
            Request(url="http://foo.example/?PHPSESSIONID=11111&foo=baz")
        )
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/discarded") == 2
    # a rule for a different domain isn't applied
    assert (
        mw.process_request(Request(url="http://foo.example/?bbn=11111&foo=baz")) is None
    )
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/allowed") == 3

    assert mw.process_request(Request(url="http://bar.example/?foo=baz")) is None
    # a universal rule isn't applied
    assert (
        mw.process_request(
            Request(url="http://bar.example/?PHPSESSIONID=11111&foo=baz")
        )
        is None
    )
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/allowed") == 5
    # removing an argument (via a domain rule)
    with pytest.raises(
        IgnoreRequest,
        match=re.escape(
            "Duplicate URL discarded: http://bar.example/?bbn=11111&foo=baz (canonical URL: http://bar.example/?foo=baz)"
        ),
    ):
        mw.process_request(Request(url="http://bar.example/?bbn=11111&foo=baz"))
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/discarded") == 3

    # skipping via dont_filter=True
    assert (
        mw.process_request(
            Request(url="http://bar.example/?bbn=11111&foo=baz", dont_filter=True)
        )
        is None
    )
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/skipped") is None
    # skipping via dud=False
    assert (
        mw.process_request(
            Request(url="http://bar.example/?bbn=11111&foo=baz", meta={"dud": False})
        )
        is None
    )
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/skipped") == 1
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/allowed") == 5

    # the method and body values are considered in the fingerprint
    assert (
        mw.process_request(Request(url="http://foo.example/?foo=bar", method="POST"))
        is None
    )
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/allowed") == 6
    assert (
        mw.process_request(
            Request(url="http://foo.example/?foo=bar", method="POST", body="body")
        )
        is None
    )
    assert mw.crawler.stats.get_value("duplicate_url_discarder/request/allowed") == 7
    with pytest.raises(
        IgnoreRequest,
        match=re.escape(
            "Duplicate URL discarded: http://foo.example/?PHPSESSIONID=11111&foo=bar (canonical URL: http://foo.example/?foo=bar)"
        ),
    ):
        mw.process_request(
            Request(
                url="http://foo.example/?PHPSESSIONID=11111&foo=bar",
                method="POST",
                body="body",
            )
        )
