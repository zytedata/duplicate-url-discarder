import json
import logging
from pathlib import Path

import pytest

from duplicate_url_discarder.url_canonicalizer import UrlCanonicalizer


def test_url_canonicalizer_empty():
    url_canonicalizer = UrlCanonicalizer([])
    assert url_canonicalizer.process_url("http://foo.example") == "http://foo.example"


def test_url_canonicalizer_load(tmp_path):
    empty_path = Path(tmp_path) / "empty.json"
    empty_path.write_text("[]")
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
    url_canonicalizer = UrlCanonicalizer([str(empty_path), rules_path])
    assert len(url_canonicalizer.processors) == 2
    assert (
        url_canonicalizer.process_url("http://foo.example/?foo=1&bbn=1&PHPSESSIONID=1")
        == "http://foo.example/?foo=1&bbn=1"
    )
    assert (
        url_canonicalizer.process_url("http://bar.example/?foo=1&bbn=1&PHPSESSIONID=1")
        == "http://bar.example/?foo=1&PHPSESSIONID=1"
    )


def test_url_canonicalizer_unknown_processor(tmp_path):
    rules_path = Path(tmp_path) / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "args": [],
                    "order": 100,
                    "processor": "unknown",
                    "urlPattern": {"include": []},
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
    with pytest.raises(ValueError, match="No URL processor named unknown"):
        UrlCanonicalizer([rules_path])


@pytest.mark.parametrize(
    ["order1", "order2"],
    [
        (1, 1),
        (1, 2),
        (2, 1),
    ],
)
def test_url_canonicalizer_multiple_rules_same_processor(tmp_path, order1, order2):
    rules_path = Path(tmp_path) / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "args": ["bbn", "ref"],
                    "order": order1,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["ref", "utm_source"],
                    "order": order2,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": []},
                },
            ]
        )
    )
    url_canonicalizer = UrlCanonicalizer([rules_path])
    assert len(url_canonicalizer.processors) == 2
    assert (
        url_canonicalizer.process_url("https://example.com?utm_source=cat&bbn=1&ref=g")
        == "https://example.com"
    )


def test_url_canonicalizer_duplicate_rules(tmp_path, caplog):
    rules_path = Path(tmp_path) / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "args": ["bbn", "ref"],
                    "order": 1,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["ref", "utm_source"],
                    "order": 2,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["ref", "utm_source"],
                    "order": 3,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["bbn", "ref"],
                    "order": 1,
                    "processor": "queryRemoval",
                    "urlPattern": {"include": []},
                },
            ]
        )
    )
    with caplog.at_level(logging.INFO):
        url_canonicalizer = UrlCanonicalizer([rules_path])
    assert len(url_canonicalizer.processors) == 3
    assert "Loaded 3 rules, skipped 1 duplicates." in caplog.text
