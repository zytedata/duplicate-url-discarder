import json
import operator
from pathlib import Path
from typing import List

from duplicate_url_discarder._rule import UrlRule, load_rules
from duplicate_url_discarder.policies import PolicyBase, get_policy


class Processor:
    def __init__(self, policy_paths: List[str]) -> None:
        rules: List[UrlRule] = []
        for policy_path in policy_paths:
            data = json.loads(Path(policy_path).read_bytes())
            rules.extend(load_rules(data))
        rules.sort(key=operator.attrgetter("order"))
        self.policies: List[PolicyBase] = [get_policy(rule) for rule in rules]

    def process_url(self, url: str) -> str:
        for policy in self.policies:
            url = policy.process(url)
        return url
