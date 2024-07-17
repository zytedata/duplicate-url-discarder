from dataclasses import dataclass

import pytest
from itemadapter import ItemAdapter

from duplicate_url_discarder.utils import item_signature, load_keys_from_path


class Object1:
    pass


class Object2:
    pass


def test_load_keys_from_path() -> None:
    assert load_keys_from_path({}) == {}

    mapping = {"tests.test_utils.Object1": "object1", Object2: "object2"}
    assert load_keys_from_path(mapping) == {Object1: "object1", Object2: "object2"}

    with pytest.raises(
        ValueError, match="Error loading object 'does-not-exist': not a full path"
    ):
        load_keys_from_path({"does-not-exist": True})


def test_item_signature() -> None:
    @dataclass
    class FakeItem:
        name: str

    value = "fake_item"
    item = FakeItem(value)
    adapter = ItemAdapter(item)

    assert item_signature(adapter, ["name"]) == hash(value)

    exception_text = (
        "Got type <class 'tests.test_utils.test_item_signature.<locals>.FakeItem'> "
        "but expected ItemAdapter."
    )
    with pytest.raises(ValueError, match=exception_text):
        item_signature(item, ["name"])  # type: ignore
