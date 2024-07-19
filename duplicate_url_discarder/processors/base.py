from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple


class UrlProcessorBase(ABC):
    def __init__(self, args: Optional[Tuple[Any, ...]] = None):
        self.args: Tuple[Any, ...] = args or ()
        self.validate_args()

    def validate_args(self) -> None:  # noqa: B027
        """Check that the processor arguments are valid, raise an exception if not."""
        pass

    @abstractmethod
    def process(self, input_url: str) -> str:
        """Return the input URL, modified according to the rules."""
