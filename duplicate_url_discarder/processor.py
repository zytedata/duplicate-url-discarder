import operator
import os
from pathlib import Path
from typing import Iterable, List, Union

from url_matcher import URLMatcher

from duplicate_url_discarder._rule import UrlRule, load_rules
from duplicate_url_discarder.policies import PolicyBase, get_policy


class Processor:
    def __init__(self, policy_paths: Iterable[Union[str, os.PathLike]]) -> None:
        rules: List[UrlRule] = []
        for policy_path in policy_paths:
            data = Path(policy_path).read_text()
            rules.extend(load_rules(data))
        rules.sort(key=operator.attrgetter("order"))
        self.url_matcher = URLMatcher()
        self.policies: List[PolicyBase] = []
        policy_id = 0
        for rule in rules:
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
