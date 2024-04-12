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
        "foo.example"
      ]
    }
  },
  {
    "order": 200,
    "policy": "pathRemoval",
    "urlPattern": {
      "exclude": [
        "foo.example/live"
      ],
      "include": [
        "foo.example"
      ]
    }
  },
  {
    "order": 0,
    "policy": "tolower",
    "urlPattern": {
      "include": []
    }
  }
]"""


def test_load_rules():
    rules = load_rules(saved_rules)
    assert rules == [
        UrlRule(100, Patterns(["foo.example"]), "queryRemoval", ("bbn", "node")),
        UrlRule(
            200, Patterns(["foo.example"], ["foo.example/live"]), "pathRemoval", ()
        ),
        UrlRule(0, Patterns([]), "tolower", ()),
    ]


def test_save_rules():
    rules = [
        UrlRule(100, Patterns(["foo.example"]), "queryRemoval", ("bbn", "node")),
        UrlRule(
            200, Patterns(["foo.example"], ["foo.example/live"]), "pathRemoval", ()
        ),
        UrlRule(0, Patterns([]), "tolower", ()),
    ]
    assert save_rules(rules) == saved_rules


def test_load_rules_null_args():
    saved_rules = """[
  {
    "order": 0,
    "args": null,
    "policy": "tolower",
    "urlPattern": {
      "include": []
    }
  }
]"""
    assert load_rules(saved_rules) == [
        UrlRule(0, Patterns([]), "tolower", ()),
    ]
