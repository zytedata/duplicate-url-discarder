from url_matcher import Patterns

from duplicate_url_discarder import UrlRule, load_rules, save_rules

saved_rules = """[
  {
    "args": [
      "bbn",
      "node"
    ],
    "order": 100,
    "policy": "queryRemoval",
    "urlPattern": {
      "include": [
        "amazon.com"
      ]
    }
  },
  {
    "args": null,
    "order": 200,
    "policy": "pathRemoval",
    "urlPattern": {
      "exclude": [
        "amazon.com/live"
      ],
      "include": [
        "amazon.com"
      ]
    }
  }
]"""


def test_load_rules():
    rules = load_rules(saved_rules)
    assert rules == [
        UrlRule(100, Patterns(["amazon.com"]), "queryRemoval", ["bbn", "node"]),
        UrlRule(
            200, Patterns(["amazon.com"], ["amazon.com/live"]), "pathRemoval", None
        ),
    ]


def test_save_rules():
    rules = [
        UrlRule(100, Patterns(["amazon.com"]), "queryRemoval", ["bbn", "node"]),
        UrlRule(
            200, Patterns(["amazon.com"], ["amazon.com/live"]), "pathRemoval", None
        ),
    ]
    assert save_rules(rules) == saved_rules
