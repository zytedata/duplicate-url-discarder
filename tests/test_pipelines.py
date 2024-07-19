from dataclasses import dataclass

from pytest_twisted import ensureDeferred
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.utils.test import get_crawler


@ensureDeferred
async def test_duplicate_url_discarder_pipeline_no_addon(caplog) -> None:
    caplog.set_level("INFO")

    class FakeSpider(Spider):
        name = "fake_spider"
        start_urls = ["data:,"]

    crawler: Crawler = get_crawler(FakeSpider, {})
    await crawler.crawl()
    assert any(
        True
        for record in caplog.records
        if "Enabled item pipelines:\n[]" in record.message
    )


@ensureDeferred
async def test_duplicate_url_discarder_pipeline_with_addon(caplog) -> None:
    caplog.set_level("INFO")

    @dataclass
    class FakeItem:
        name: str
        value: int

    class FakeSpider(Spider):
        name = "fake_spider"
        start_urls = ["data:,"]

        def parse(self, response):
            yield FakeItem(name="AAA", value=0)
            yield FakeItem(name="BBB", value=1)
            yield FakeItem(name="AAA", value=2)  # dropped

            # These aren't declared in DUD_ATTRIBUTES_PER_ITEM, so they aren't dropped
            yield {"name": "CCC", "value": 3}
            yield {"name": "CCC", "value": 4}

    settings = {
        "DUD_ATTRIBUTES_PER_ITEM": {FakeItem: ["name"]},
        "ADDONS": {
            "duplicate_url_discarder.Addon": 600,
        },
    }
    crawler: Crawler = get_crawler(FakeSpider, settings)
    await crawler.crawl()

    expected_text = "Enabled item pipelines:\n[<class 'duplicate_url_discarder.pipelines.DuplicateUrlDiscarderPipeline'>]"
    messages = [record.message for record in caplog.records]
    assert any(True for record in caplog.records if expected_text in messages)

    assert crawler.stats.get_value("item_scraped_count") == 4
    assert crawler.stats.get_value("item_dropped_count") == 1

    dropped_messages = [
        record.message
        for record in caplog.records
        if "Dropping item that was already seen before" in record.message
    ]
    assert len(dropped_messages) == 1
    assert "FakeItem(name='AAA', value=2)" in dropped_messages[0]
