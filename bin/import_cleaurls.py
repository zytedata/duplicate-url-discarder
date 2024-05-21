import re
import string
import sys
from pathlib import Path
from typing import List

import requests
from url_matcher import Patterns

from duplicate_url_discarder.rule import UrlRule, save_rules


def _expander(s):
    # https://stackoverflow.com/a/20061999/113586
    from itertools import product

    pat = r"\(([^)]*)\)"
    pieces = re.split(pat, s)
    pieces = [piece.split("|") for piece in pieces]
    for p in product(*pieces):
        yield "".join(p)


def main():
    url = "https://rules2.clearurls.xyz/data.minify.json"
    r = requests.get(url)
    data = r.json()
    rules: List[UrlRule] = []
    for provider in data["providers"].values():
        url_re: str = provider["urlPattern"]
        include_patterns: List[str] = []
        if url_re != ".*":
            url_re = re.sub(
                "^" + re.escape(r"^https?:\/\/(?:[a-z0-9-]+\.)*?"), "", url_re
            )  # scheme and subdomains
            url_re = re.sub(
                "^" + re.escape(r"^https?://(?:[a-z0-9-]+\.)*?"), "", url_re
            )  # scheme and subdomains
            url_re = re.sub(re.escape(r"(?:\.[a-z]{2,}){1,}") + "$", "", url_re)  # TLDs
            url_re = url_re.replace(r"^https?:\/\/", "")  # scheme
            url_re = url_re.replace("(?:", "(")  # non-capturing group markers
            remaining_special_chars = set(url_re) - set(
                string.ascii_letters + string.digits + "-.\\/"
            )
            if remaining_special_chars <= set("(|)"):
                if "|" in url_re:
                    include_patterns = list(_expander(url_re))
                else:
                    include_patterns = [url_re]
                # cautious unquoting
                unquote_chars = (".", "/", "-")
                for i in range(len(include_patterns)):
                    for c in unquote_chars:
                        include_patterns[i] = include_patterns[i].replace(rf"\{c}", c)
                    if "\\" in include_patterns[i]:
                        print(f"Incomplete cleanup 2: {include_patterns[i]}")
                        continue
            else:
                print(f"Incomplete cleanup 1: {url_re}")
                include_patterns = [url_re]
        # not sure if the latter is always included in the former
        params_to_remove: List[str] = provider.get("rules", []) + provider.get(
            "referralMarketing", []
        )
        params_to_remove = [s.replace(r"(?:%3F)?", "") for s in params_to_remove]
        rules.append(
            UrlRule(
                0, Patterns(include_patterns), "queryRemoval", tuple(params_to_remove)
            )
        )
    rules_json = save_rules(rules)
    outfile = Path(sys.argv[1] if len(sys.argv) > 1 else "rules.json")
    outfile.write_text(rules_json)


if __name__ == "__main__":
    main()
