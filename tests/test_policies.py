import pytest
from url_matcher import Patterns

from duplicate_url_discarder import UrlRule
from duplicate_url_discarder.policies import PolicyBase, QueryRemovalPolicy, get_policy


class HardcodedPolicy(PolicyBase):
    def process(self, url: str) -> str:
        return "http://hardcoded.example"


def test_get_policy():
    pattern = Patterns([])
    args = ["foo", "bar"]

    rule = UrlRule(0, pattern, "queryRemoval", args)
    policy = get_policy(rule)
    assert type(policy) is QueryRemovalPolicy
    assert policy.args == args

    rule = UrlRule(0, pattern, "tests.test_policies.HardcodedPolicy", args)
    policy = get_policy(rule)
    assert type(policy) is HardcodedPolicy
    assert policy.args == args

    rule = UrlRule(0, pattern, "unknown", args)
    with pytest.raises(ValueError, match="No policy named unknown"):
        get_policy(rule)


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
    policy = QueryRemovalPolicy(args)
    assert policy.process(url) == expected


def test_query_removal_validate_args():
    with pytest.raises(TypeError, match="strings, not <class 'bytes'>: b''"):
        QueryRemovalPolicy([b""])
    with pytest.raises(TypeError, match="strings, not <class 'NoneType'>: None"):
        QueryRemovalPolicy(["a", None, ""])
    QueryRemovalPolicy([""])
    QueryRemovalPolicy([])
