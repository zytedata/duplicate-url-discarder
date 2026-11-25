from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class UrlProcessorBase(ABC):
    def __init__(self, args: tuple[Any, ...] | None = None):
        self.args: tuple[Any, ...] = args or ()
        self.validate_args()

    def validate_args(self) -> None:  # noqa: B027
        """Check that the processor arguments are valid, raise an exception if not."""

    @abstractmethod
    def process(self, input_url: str) -> str:
        """Return the input URL, modified according to the rules."""
