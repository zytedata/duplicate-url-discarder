from __future__ import annotations

from collections.abc import Iterable
from typing import Any, TypeVar

from itemadapter import ItemAdapter
from scrapy.utils.misc import load_object

T = TypeVar("T")


def load_keys_from_path(mapping: dict[Any, T]) -> dict[Any, T]:
    """Given a mapping, convert the keys that represent import paths
    into their respective objects.
    """
    new_mapping = {}
    for cls_or_path, values in mapping.items():
        cls = load_object(cls_or_path) if isinstance(cls_or_path, str) else cls_or_path
        new_mapping[cls] = values
    return new_mapping


def item_signature(item: ItemAdapter, item_attributes: Iterable[str]) -> int:
    try:
        values = [f"{attrib}:{item.get(attrib)}" for attrib in item_attributes]
    except AttributeError as error:
        raise ValueError(f"Got type {type(item)} but expected ItemAdapter.") from error
    return hash("|".join(values))
