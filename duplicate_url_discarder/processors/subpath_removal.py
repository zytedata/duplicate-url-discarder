import re
from collections.abc import Iterable

from scrapy.utils.url import parse_url

from .base import UrlProcessorBase


class SubpathRemovalProcessor(UrlProcessorBase):
    """Removes the i-th subpath (starts at 0) from the URL path if it exists.

    An example would be removing the 0-th and 2nd subpath of a URL like
    https://example.com/a/b/c/d would result in https://example.com/b/d.
    """

    def validate_args(self) -> None:
        base_exception_msg = "subpathRemoval args must be an iterable of integers."

        if not isinstance(self.args, Iterable):
            raise TypeError(
                f"{base_exception_msg} Got type: {type(self.args)}: {self.args}."
            )

        for arg in self.args:
            if not isinstance(arg, int):
                raise ValueError(
                    f"{base_exception_msg} Encountered {type(arg)}: {arg}."
                )

    def process(self, input_url: str) -> str:
        parsed_url = parse_url(input_url)
        subpaths = re.findall(r"/[^/]*", parsed_url.path)
        path = "".join(
            subpath for i, subpath in enumerate(subpaths) if i not in self.args
        )
        return parsed_url._replace(path=path).geturl()
