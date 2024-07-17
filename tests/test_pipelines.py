from dataclasses import dataclass

from pytest_twisted import ensureDeferred
from scrapy import Spider
from scrapy.crawler import Crawler
from scrapy.utils.test import get_crawler


@ensureDeferred
async def test_duplicate_url_discarder_pipeline_no_addon(caplog, httpserver) -> None:
    caplog.set_level("INFO")

    httpserver.expect_request("")
    start_url = httpserver.url_for("")

    class FakeSpider(Spider):
        name = "fake_spider"
        start_urls = [start_url]

    crawler: Crawler = get_crawler(FakeSpider, {})
    await crawler.crawl()
    assert any(
        True
        for record in caplog.records
        if "Enabled item pipelines:\n[]" in record.message
    )


@ensureDeferred
async def test_duplicate_url_discarder_pipeline_with_addon(caplog, httpserver) -> None:
    caplog.set_level("INFO")

    httpserver.expect_request("/dummy").respond_with_data("Dummy")
    start_url = httpserver.url_for("/dummy")

    @dataclass
    class FakeItem:
        name: str

    class FakeSpider(Spider):
        name = "fake_spider"
        start_urls = [start_url]

        def parse(self, response):
            yield FakeItem(name="AAA")
            yield FakeItem(name="BBB")
            yield FakeItem(name="AAA")  # dropped

            # These aren't declared in DUD_ATTRIBUTES_PER_ITEM so they aren't drpoped
            yield {"name": "CCC"}
            yield {"name": "CCC"}

    settings = {
        "DUD_ATTRIBUTES_PER_ITEM": {FakeItem: ["name"]},
        "ADDONS": {
            "duplicate_url_discarder.Addon": 600,
        },
    }
    crawler: Crawler = get_crawler(FakeSpider, settings)
    await crawler.crawl()

    expected_text = "Enabled item pipelines:\n['duplicate_url_discarder.DuplicateUrlDiscarderPipeline']"
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