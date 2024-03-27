from abc import ABC, abstractmethod
from typing import Any

from url_matcher import Patterns, URLMatcher


class PolicyBase(ABC):
    def __init__(self, url_pattern: Patterns, args: Any):
        self.url_matcher: URLMatcher = URLMatcher({0: url_pattern})
        self.args: Any = args
        self.validate_args()

    def process(self, input_url: str) -> str:
        """Return the input URL, modified according to the rules if applicable."""
        if not self.is_applicable(input_url):
            return input_url
        return self.modify_url(input_url)

    def validate_args(self) -> None:  # noqa: B027
        """Check that the policy arguments are valid, raise an exception if not."""
        pass

    def is_applicable(self, input_url: str) -> bool:
        """Return True if the policy should handle this URL, False otherwise."""
        return self.url_matcher.match(input_url) is not None

    @abstractmethod
    def modify_url(self, input_url: str) -> str:
        """Return the input URL, modified according to the rules."""
