from typing import Dict, Type

from scrapy.utils.misc import load_object

from duplicate_url_discarder._rule import UrlRule

from .base import PolicyBase
from .query_removal import QueryRemovalPolicy

_POLICY_CLASSES: Dict[str, Type[PolicyBase]] = {
    "queryRemoval": QueryRemovalPolicy,
}


def get_policy(rule: UrlRule) -> PolicyBase:
    policy_cls: Type[PolicyBase]
    if "." not in rule.policy:
        if rule.policy not in _POLICY_CLASSES:
            raise ValueError(f"No policy named {rule.policy}")
        policy_cls = _POLICY_CLASSES[rule.policy]
    else:
        policy_cls = load_object(rule.policy)
    return policy_cls(rule.args)
