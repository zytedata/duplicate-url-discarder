import re

from scrapy.utils.url import parse_url

from .base import UrlProcessorBase


class NormalizerProcessor(UrlProcessorBase):
    def validate_args(self) -> None:
        if self.args:
            raise TypeError(f"normalizeUrl doesn't accept args, got: {self.args}")

    def process(self, input_url: str) -> str:
        """Normalizes the input URL by removing the following:

        * 'www.' prefixes including ones with numerical characters, e.g. 'www2.'
        * trailing slashes
        """

        parsed_url = parse_url(input_url)
        netloc = re.sub(r"^www\d*\.", "", parsed_url.netloc)
        path = parsed_url.path.rstrip("/")
        return parsed_url._replace(netloc=netloc, path=path).geturl()
