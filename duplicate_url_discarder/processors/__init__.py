from __future__ import annotations

from ..rule import UrlRule
from .base import UrlProcessorBase
from .normalize import NormalizerProcessor
from .query_removal import QueryRemovalProcessor
from .query_removal_except import QueryRemovalExceptProcessor
from .subpath_removal import SubpathRemovalProcessor

_PROCESSOR_CLASSES: dict[str, type[UrlProcessorBase]] = {
    "normalizer": NormalizerProcessor,
    "queryRemoval": QueryRemovalProcessor,
    "queryRemovalExcept": QueryRemovalExceptProcessor,
    "subpathRemoval": SubpathRemovalProcessor,
}


def get_processor(rule: UrlRule) -> UrlProcessorBase:
    processor_cls: type[UrlProcessorBase]
    if rule.processor not in _PROCESSOR_CLASSES:
        raise ValueError(f"No URL processor named {rule.processor}")
    processor_cls = _PROCESSOR_CLASSES[rule.processor]
    return processor_cls(rule.args)
