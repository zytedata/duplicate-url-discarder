from scrapy import Spider
from scrapy.settings import BaseSettings
from scrapy.settings.default_settings import (
    REQUEST_FINGERPRINTER_CLASS as _SCRAPY_DEFAULT_REQUEST_FINGEPRINTER_CLASS,
)
from scrapy.utils.request import RequestFingerprinter
from scrapy.utils.test import get_crawler

from duplicate_url_discarder import Addon


def test_addon():
    settings_dict = {
        "ADDONS": {
            Addon: 600,
        },
    }
    crawler = get_crawler(Spider, settings_dict)
    assert (
        crawler.settings["REQUEST_FINGERPRINTER_CLASS"]
        == "duplicate_url_discarder.Fingerprinter"
    )
    assert (
        crawler.settings["DUD_FALLBACK_REQUEST_FINGERPRINTER_CLASS"]
        == _SCRAPY_DEFAULT_REQUEST_FINGEPRINTER_CLASS
    )


def test_addon_fallback():
    class AnotherFingerprinter(RequestFingerprinter):
        pass

    class AnotherAddon:
        def update_settings(self, settings: BaseSettings) -> None:
            settings.set(
                "REQUEST_FINGERPRINTER_CLASS",
                AnotherFingerprinter,
                "addon",
            )

    settings_dict = {
        "ADDONS": {
            AnotherAddon: 500,
            Addon: 600,
        },
    }
    crawler = get_crawler(Spider, settings_dict)
    assert (
        crawler.settings["REQUEST_FINGERPRINTER_CLASS"]
        == "duplicate_url_discarder.Fingerprinter"
    )
    assert (
        crawler.settings["DUD_FALLBACK_REQUEST_FINGERPRINTER_CLASS"]
        == AnotherFingerprinter
    )
