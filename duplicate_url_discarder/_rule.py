import json
from dataclasses import dataclass
from typing import Any, Dict, List

from url_matcher import Patterns


@dataclass
class PolicyRule:
    order: int
    url_pattern: Patterns
    policy: str
    args: Any


def load_rules(data: str) -> List[PolicyRule]:
    """Load a list of policy rules from a JSON text."""
    results: List[PolicyRule] = []
    j = json.loads(data)
    for item in j:
        results.append(_rule_from_dict(item))
    return results


def save_rules(policies: List[PolicyRule]) -> str:
    """Save a list of policy rules to a JSON text."""
    return json.dumps(
        [_rule_to_dict(p) for p in policies],
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )


def _rule_to_dict(policy: PolicyRule) -> Dict[str, Any]:
    """Save a policy rule to a dict"""
    pattern = {"include": list(policy.url_pattern.include)}
    if policy.url_pattern.exclude:
        pattern["exclude"] = list(policy.url_pattern.exclude)
    return {
        "order": policy.order,
        "urlPattern": pattern,
        "policy": policy.policy,
        "args": policy.args,
    }


def _rule_from_dict(policy_dict: Dict[str, Any]) -> PolicyRule:
    """Load a policy rule from a dict"""

    return PolicyRule(
        order=policy_dict["order"],
        url_pattern=Patterns(**policy_dict["urlPattern"]),
        policy=policy_dict["policy"],
        args=policy_dict.get("args"),
    )
