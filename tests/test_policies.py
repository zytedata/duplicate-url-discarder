import pytest
from url_matcher import Patterns

from duplicate_url_discarder import UrlRule
from duplicate_url_discarder.policies import PolicyBase, QueryRemovalPolicy, get_policy


class HardcodedPolicy(PolicyBase):
    def modify_url(self, url: str) -> str:
        return "http://hardcoded.example"


def test_get_policy():
    pattern = Patterns(["foo"], ["bar", "baz"])
    args = ["foo", "bar"]

    rule = UrlRule(0, pattern, "queryRemoval", args)
    policy = get_policy(rule)
    assert type(policy) is QueryRemovalPolicy
    assert policy.args == args
    assert policy.url_matcher.get(0) == pattern

    rule = UrlRule(0, pattern, "tests.test_policies.HardcodedPolicy", args)
    policy = get_policy(rule)
    assert type(policy) is HardcodedPolicy
    assert policy.args == args
    assert policy.url_matcher.get(0) == pattern

    rule = UrlRule(0, pattern, "unknown", args)
    with pytest.raises(ValueError, match="No policy named unknown"):
        get_policy(rule)


@pytest.mark.parametrize(
    ["url", "expected"],
    [
        ("http://foo.example", "http://foo.example"),
        ("http://bar.example", "http://hardcoded.example"),
        ("http://foo.bar.example", "http://foo.bar.example"),
        ("http://foobar.example", "http://foobar.example"),
        ("http://bar.examplee", "http://bar.examplee"),
    ],
)
def test_url_pattern(url, expected):
    policy = HardcodedPolicy(
        url_pattern=Patterns(include=["bar.example"], exclude=["foo.bar.example"]),
        args=None,
    )
    assert policy.process(url) == expected


@pytest.mark.parametrize(
    ["args", "url", "expected"],
    [
        ([], "http://foo.example?foo=1&bar", "http://foo.example?foo=1&bar"),
        (["a"], "http://foo.example?foo=1&bar", "http://foo.example?foo=1&bar"),
        (["foo"], "http://foo.example?foo=1&bar", "http://foo.example?bar"),
        (["bar"], "http://foo.example?foo=1&bar", "http://foo.example?foo=1"),
        (
            ["bar"],
            "http://foo.example?foo=1&foo=2&bar&bar=1",
            "http://foo.example?foo=1&foo=2",
        ),
        (
            ["bar"],
            "http://foo.example?foo=1&bar#bar=frag",
            "http://foo.example?foo=1#bar=frag",
        ),
        (["foo", "baz"], "http://foo.example?foo=1&bar", "http://foo.example?bar"),
        (["foo", "bar"], "http://foo.example?foo=1&bar", "http://foo.example"),
    ],
)
def test_query_removal(args, url, expected):
    policy = QueryRemovalPolicy(Patterns([]), args)
    assert policy.process(url) == expected


def test_query_removal_validate_args():
    p = Patterns([])
    with pytest.raises(TypeError, match="strings, not <class 'bytes'>: b''"):
        QueryRemovalPolicy(p, [b""])
    with pytest.raises(TypeError):
        QueryRemovalPolicy(p, ["a", None, ""])
    QueryRemovalPolicy(p, [""])
    QueryRemovalPolicy(p, [])
