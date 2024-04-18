import json
import logging
from pathlib import Path

import pytest

from duplicate_url_discarder import UrlCanonicalizer


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
                    "policy": "queryRemoval",
                    "urlPattern": {"include": ["bar.example"]},
                },
                {
                    "args": ["PHPSESSIONID"],
                    "order": 1,
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
            ]
        )
    )
    url_canonicalizer = UrlCanonicalizer([str(empty_path), rules_path])
    assert len(url_canonicalizer.policies) == 2
    assert (
        url_canonicalizer.process_url("http://foo.example/?foo=1&bbn=1&PHPSESSIONID=1")
        == "http://foo.example/?foo=1&bbn=1"
    )


def test_url_canonicalizer_unknown_policy(tmp_path):
    rules_path = Path(tmp_path) / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "args": [],
                    "order": 100,
                    "policy": "unknown",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["PHPSESSIONID"],
                    "order": 1,
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
            ]
        )
    )
    with pytest.raises(ValueError, match="No policy named unknown"):
        UrlCanonicalizer([rules_path])


@pytest.mark.parametrize(
    ["order1", "order2"],
    [
        (1, 1),
        (1, 2),
        (2, 1),
    ],
)
def test_url_canonicalizer_multiple_rules_same_policy(tmp_path, order1, order2):
    rules_path = Path(tmp_path) / "rules.json"
    rules_path.write_text(
        json.dumps(
            [
                {
                    "args": ["bbn", "ref"],
                    "order": order1,
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["ref", "utm_source"],
                    "order": order2,
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
            ]
        )
    )
    url_canonicalizer = UrlCanonicalizer([rules_path])
    assert len(url_canonicalizer.policies) == 2
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
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["ref", "utm_source"],
                    "order": 2,
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["ref", "utm_source"],
                    "order": 3,
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
                {
                    "args": ["bbn", "ref"],
                    "order": 1,
                    "policy": "queryRemoval",
                    "urlPattern": {"include": []},
                },
            ]
        )
    )
    with caplog.at_level(logging.INFO):
        url_canonicalizer = UrlCanonicalizer([rules_path])
    assert len(url_canonicalizer.policies) == 3
    assert "Loaded 3 rules, skipped 1 duplicates." in caplog.text
