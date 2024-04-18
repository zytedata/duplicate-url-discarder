import logging
import operator
import os
from pathlib import Path
from typing import Iterable, List, Set, Union

from url_matcher import URLMatcher

from ._rule import UrlRule, load_rules
from .policies import PolicyBase, get_policy

logger = logging.getLogger(__name__)


class UrlCanonicalizer:
    def __init__(self, policy_paths: Iterable[Union[str, os.PathLike]]) -> None:
        rules: Set[UrlRule] = set()
        full_rule_count = 0
        for policy_path in policy_paths:
            data = Path(policy_path).read_text()
            loaded_rules = load_rules(data)
            full_rule_count += len(loaded_rules)
            rules.update(loaded_rules)
        rule_count = len(rules)
        logger.info(
            f"Loaded {rule_count} rules, skipped {full_rule_count - rule_count} duplicates."
        )

        self.url_matcher = URLMatcher()
        self.policies: List[PolicyBase] = []
        policy_id = 0
        for rule in sorted(rules, key=operator.attrgetter("order")):
            policy = get_policy(rule)
            self.policies.append(policy)
            self.url_matcher.add_or_update(policy_id, rule.url_pattern)
            policy_id += 1

    def process_url(self, url: str) -> str:
        use_universal = True
        for policy_id in self.url_matcher.match_all(url, include_universal=False):
            use_universal = False
            policy = self.policies[policy_id]
            url = policy.process(url)
        if use_universal:
            for policy_id in self.url_matcher.match_universal():
                policy = self.policies[policy_id]
                url = policy.process(url)
        return url
