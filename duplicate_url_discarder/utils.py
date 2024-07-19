from typing import Any, Dict, Iterable, TypeVar

from itemadapter import ItemAdapter
from scrapy.utils.misc import load_object

T = TypeVar("T")


def load_keys_from_path(mapping: Dict[Any, T]) -> Dict[Any, T]:
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
    except AttributeError:
        raise ValueError(f"Got type {type(item)} but expected ItemAdapter.")
    return hash("|".join(values))
