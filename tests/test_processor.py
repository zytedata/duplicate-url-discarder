import json
from pathlib import Path

import pytest

from duplicate_url_discarder import Processor


def test_processor_empty():
    processor = Processor([])
    assert processor.process_url("http://foo.example") == "http://foo.example"


def test_processor_load(tmp_path):
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
                    "urlPattern": {"include": ["amazon.com"]},
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
    processor = Processor([str(empty_path), rules_path])
    assert len(processor.policies) == 2
    assert (
        processor.process_url("http://foo.example/?foo=1&bbn=1&PHPSESSIONID=1")
        == "http://foo.example/?foo=1&bbn=1"
    )


def test_processor_unknown_policy(tmp_path):
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
        Processor([rules_path])
