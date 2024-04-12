from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from url_matcher import Patterns

if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self


@dataclass(frozen=True)
class UrlRule:
    order: int
    url_pattern: Patterns
    policy: str
    args: Tuple[Any, ...]

    @classmethod
    def from_dict(cls, policy_dict: Dict[str, Any]) -> Self:
        """Load a rule from a dict"""
        return cls(
            order=policy_dict["order"],
            url_pattern=Patterns(**policy_dict["urlPattern"]),
            policy=policy_dict["policy"],
            args=tuple(policy_dict.get("args") or ()),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Save a rule to a dict"""
        pattern = {"include": list(self.url_pattern.include)}
        if self.url_pattern.exclude:
            pattern["exclude"] = list(self.url_pattern.exclude)
        result = {
            "order": self.order,
            "urlPattern": pattern,
            "policy": self.policy,
        }
        if self.args:
            result["args"] = list(self.args)
        return result


def load_rules(data: str) -> List[UrlRule]:
    """Load a list of rules from a JSON text."""
    results: List[UrlRule] = []
    j = json.loads(data)
    for item in j:
        results.append(UrlRule.from_dict(item))
    return results


def save_rules(policies: List[UrlRule]) -> str:
    """Save a list of rules to a JSON text."""
    return json.dumps(
        [p.to_dict() for p in policies],
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
