from scrapy.settings import BaseSettings
from scrapy.utils.misc import load_object

from duplicate_url_discarder.pipelines import DuplicateUrlDiscarderPipeline


def _setdefault(settings, setting, cls, pos) -> None:
    setting_value = settings[setting]
    if not setting_value:
        settings[setting] = {cls: pos}
        return None
    if cls in setting_value:
        return None
    for cls_or_path in setting_value:
        if isinstance(cls_or_path, str):
            _cls = load_object(cls_or_path)
            if _cls == cls:
                return None
    settings[setting][cls] = pos


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
        _setdefault(
            settings,
            "ITEM_PIPELINES",
            DuplicateUrlDiscarderPipeline,
            100,
        )
