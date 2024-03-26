from w3lib.url import url_query_cleaner

from .base import PolicyBase


class QueryRemovalPolicy(PolicyBase):
    def validate_args(self) -> None:
        for arg in self.args:
            if not isinstance(arg, str):
                raise TypeError(
                    f"queryRemoval args must be strings, not {type(arg)}: {arg}"
                )

    def _process(self, input_url: str) -> str:
        args_to_remove = self.args
        return url_query_cleaner(
            input_url, args_to_remove, remove=True, unique=False, keep_fragments=True
        )
