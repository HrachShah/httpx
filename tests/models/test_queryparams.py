import pytest

import httpx


@pytest.mark.parametrize(
    "source",
    [
        "a=123&a=456&b=789",
        {"a": ["123", "456"], "b": 789},
        {"a": ("123", "456"), "b": 789},
        [("a", "123"), ("a", "456"), ("b", "789")],
        (("a", "123"), ("a", "456"), ("b", "789")),
    ],
)
def test_queryparams(source):
    q = httpx.QueryParams(source)
    assert "a" in q
    assert "A" not in q
    assert "c" not in q
    assert q["a"] == "123"
    assert q.get("a") == "123"
    assert q.get("nope", default=None) is None
    assert q.get_list("a") == ["123", "456"]

    assert list(q.keys()) == ["a", "b"]
    assert list(q.values()) == ["123", "789"]
    assert list(q.items()) == [("a", "123"), ("b", "789")]
    assert len(q) == 2
    assert list(q) == ["a", "b"]
    assert dict(q) == {"a": "123", "b": "789"}
    assert str(q) == "a=123&a=456&b=789"
    assert repr(q) == "QueryParams('a=123&a=456&b=789')"
    assert httpx.QueryParams({"a": "123", "b": "456"}) == httpx.QueryParams(
        [("a", "123"), ("b", "456")]
    )
    assert httpx.QueryParams({"a": "123", "b": "456"}) == httpx.QueryParams(
        "a=123&b=456"
    )
    assert httpx.QueryParams({"a": "123", "b": "456"}) == httpx.QueryParams(
        {"b": "456", "a": "123"}
    )
    assert httpx.QueryParams() == httpx.QueryParams({})
    assert httpx.QueryParams([("a", "123"), ("a", "456")]) == httpx.QueryParams(
        "a=123&a=456"
    )
    assert httpx.QueryParams({"a": "123", "b": "456"}) != "invalid"

    q = httpx.QueryParams([("a", "123"), ("a", "456")])
    assert httpx.QueryParams(q) == q


def test_queryparam_types():
    q = httpx.QueryParams(None)
    assert str(q) == ""

    q = httpx.QueryParams({"a": True})
    assert str(q) == "a=true"

    q = httpx.QueryParams({"a": False})
    assert str(q) == "a=false"

    q = httpx.QueryParams({"a": ""})
    assert str(q) == "a="

    q = httpx.QueryParams({"a": None})
    assert str(q) == "a="

    q = httpx.QueryParams({"a": 1.23})
    assert str(q) == "a=1.23"

    q = httpx.QueryParams({"a": 123})
    assert str(q) == "a=123"

    q = httpx.QueryParams({"a": [1, 2]})
    assert str(q) == "a=1&a=2"


def test_empty_query_params():
    q = httpx.QueryParams({"a": ""})
    assert str(q) == "a="

    q = httpx.QueryParams("a=")
    assert str(q) == "a="

    q = httpx.QueryParams("a")
    assert str(q) == "a="


def test_queryparam_update_is_hard_deprecated():
    q = httpx.QueryParams("a=123")
    with pytest.raises(RuntimeError):
        q.update({"a": "456"})


def test_queryparam_setter_is_hard_deprecated():
    q = httpx.QueryParams("a=123")
    with pytest.raises(RuntimeError):
        q["a"] = "456"


def test_queryparam_set():
    q = httpx.QueryParams("a=123")
    q = q.set("a", "456")
    assert q == httpx.QueryParams("a=456")


def test_queryparam_add():
    q = httpx.QueryParams("a=123")
    q = q.add("a", "456")
    assert q == httpx.QueryParams("a=123&a=456")


def test_queryparam_remove():
    q = httpx.QueryParams("a=123")
    q = q.remove("a")
    assert q == httpx.QueryParams("")


def test_queryparam_merge():
    q = httpx.QueryParams("a=123")
    q = q.merge({"b": "456"})
    assert q == httpx.QueryParams("a=123&b=456")
    q = q.merge({"a": "000", "c": "789"})
    assert q == httpx.QueryParams("a=000&b=456&c=789")


def test_queryparams_are_hashable():
    params = (
        httpx.QueryParams("a=123"),
        httpx.QueryParams({"a": 123}),
        httpx.QueryParams("b=456"),
        httpx.QueryParams({"b": 456}),
    )

    assert len(set(params)) == 2


def test_queryparams_rejects_too_many_positional_args():
    """QueryParams() used to `assert len(args) < 2, "Too many arguments."`.

    Under `python -O` the assert is stripped and the second positional
    argument silently drove the rest of the constructor with whatever
    `parse_qs` would make of it (e.g. for `QueryParams("a=1", "b=2")` the
    second arg is a stray string that gets parsed as query text and
    produces confusing results). Raise a clear TypeError instead.
    """
    with pytest.raises(TypeError, match="Too many positional arguments"):
        httpx.QueryParams("a=1", "b=2")
    with pytest.raises(TypeError, match="Too many positional arguments"):
        httpx.QueryParams({"a": "1"}, {"b": "2"})


def test_queryparams_rejects_mixed_positional_and_keyword():
    """QueryParams() used to `assert not (args and kwargs), "Cannot mix named
    and unnamed arguments."`. Under `python -O` that assert is stripped
    and a call like `QueryParams("a=1", b="2")` would silently use only
    the positional argument and drop the keyword. Raise a clear TypeError
    instead.
    """
    with pytest.raises(TypeError, match="Cannot mix positional and keyword"):
        httpx.QueryParams("a=1", b="2")
    with pytest.raises(TypeError, match="Cannot mix positional and keyword"):
        httpx.QueryParams({"a": "1"}, b="2")
