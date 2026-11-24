from __future__ import annotations

import logging
import operator
import os
from collections.abc import Iterable
from pathlib import Path

from url_matcher import URLMatcher

from .processors import UrlProcessorBase, get_processor
from .rule import UrlRule, load_rules

logger = logging.getLogger(__name__)


class UrlCanonicalizer:
    def __init__(self, rule_paths: Iterable[str | os.PathLike]) -> None:
        rules: set[UrlRule] = set()
        full_rule_count = 0
        for rule_path in rule_paths:
            data = Path(rule_path).read_text()
            loaded_rules = load_rules(data)
            full_rule_count += len(loaded_rules)
            rules.update(loaded_rules)
        rule_count = len(rules)
        logger.info(
            f"Loaded {rule_count} rules, skipped {full_rule_count - rule_count} duplicates."
        )

        self.url_matcher = URLMatcher()
        self.processors: dict[int, UrlProcessorBase] = {}
        for rule_id, rule in enumerate(sorted(rules, key=operator.attrgetter("order"))):
            processor = get_processor(rule)
            self.processors[rule_id] = processor
            self.url_matcher.add_or_update(rule_id, rule.url_pattern)

    def process_url(self, url: str) -> str:
        use_universal = True
        for rule_id in self.url_matcher.match_all(url, include_universal=False):
            use_universal = False
            processor = self.processors[rule_id]
            url = processor.process(url)
        if use_universal:
            for rule_id in self.url_matcher.match_universal():
                processor = self.processors[rule_id]
                url = processor.process(url)
        return url
