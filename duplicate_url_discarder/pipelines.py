from typing import Any, Dict, Set, Tuple, TypeVar

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.exceptions import DropItem, NotConfigured

from .utils import item_signature, load_keys_from_path

T = TypeVar("T")


class DuplicateUrlDiscarderPipeline:
    def __init__(self, crawler: Crawler):
        #: A mapping of item class to a list of attribute names which will be used to
        #: compute the item signature.
        self._attributes_per_item: Dict[Any, Tuple[str, ...]] = load_keys_from_path(
            crawler.settings.getdict("DUD_ATTRIBUTES_PER_ITEM", {})
        )

        #: Record of all the item signatures that were previously processed and seen.
        self._seen_item_signatures: Set[int] = set()

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        if not crawler.settings.getdict("DUD_ATTRIBUTES_PER_ITEM"):
            raise NotConfigured(
                "Set DUD_ATTRIBUTES_PER_ITEM to enable DuplicateUrlDiscarderPipeline"
            )
        return cls(crawler)

    def process_item(self, item: T, spider: Spider) -> T:
        item_attributes = self._attributes_per_item.get(type(item))
        if not item_attributes:
            return item

        signature = item_signature(ItemAdapter(item), item_attributes)
        if signature in self._seen_item_signatures:
            raise DropItem(f"Dropping item that was already seen before:\n{item}")

        self._seen_item_signatures.add(signature)
        return item
