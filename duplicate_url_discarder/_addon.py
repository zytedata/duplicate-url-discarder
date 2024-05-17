from scrapy.settings import BaseSettings


class Addon:
    def update_settings(self, settings: BaseSettings) -> None:
        current_fpr = settings.get("REQUEST_FINGERPRINTER_CLASS")
        settings.set(
            "REQUEST_FINGERPRINTER_CLASS",
            "duplicate_url_discarder.Fingerprinter",
            settings.getpriority("REQUEST_FINGERPRINTER_CLASS"),
        )
        settings.set(
            "DUD_FALLBACK_REQUEST_FINGERPRINTER_CLASS",
            current_fpr,
            "addon",
        )
