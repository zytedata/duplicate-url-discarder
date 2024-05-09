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
    processor: str
    args: Tuple[Any, ...]

    @classmethod
    def from_dict(cls, rule_dict: Dict[str, Any]) -> Self:
        """Load a rule from a dict"""
        return cls(
            order=rule_dict["order"],
            url_pattern=Patterns(**rule_dict["urlPattern"]),
            processor=rule_dict["processor"],
            args=tuple(rule_dict.get("args") or ()),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Save a rule to a dict"""
        pattern = {"include": list(self.url_pattern.include)}
        if self.url_pattern.exclude:
            pattern["exclude"] = list(self.url_pattern.exclude)
        result = {
            "order": self.order,
            "urlPattern": pattern,
            "processor": self.processor,
        }
        if self.args:
            result["args"] = list(self.args)
        return result


def load_rules(data: str) -> List[UrlRule]:
    """Load a list of rules from a JSON text."""
    return [UrlRule.from_dict(item) for item in json.loads(data)]


def save_rules(rules: List[UrlRule]) -> str:
    """Save a list of rules to a JSON text."""
    return json.dumps(
        [r.to_dict() for r in rules],
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    )
