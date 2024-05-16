from url_matcher import Patterns

from duplicate_url_discarder.rule import UrlRule, load_rules, save_rules

saved_rules = """[
  {
    "args": [
      "bbn",
      "node"
    ],
    "order": 100,
    "processor": "queryRemoval",
    "urlPattern": {
      "include": [
        "foo.example"
      ]
    }
  },
  {
    "order": 200,
    "processor": "pathRemoval",
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
    "processor": "tolower",
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
    "processor": "tolower",
    "urlPattern": {
      "include": []
    }
  }
]"""
    assert load_rules(saved_rules) == [
        UrlRule(0, Patterns([]), "tolower", ()),
    ]


def test_load_rules_extra_fields():
    saved_rules = """[
  {
    "order": 200,
    "extra_field": "foo",
    "processor": "pathRemoval",
    "urlPattern": {
      "exclude": [
        "foo.example/live"
      ],
      "include": [
        "foo.example"
      ]
    }
  }
]"""
    assert load_rules(saved_rules) == [
        UrlRule(
            200, Patterns(["foo.example"], ["foo.example/live"]), "pathRemoval", ()
        ),
    ]
