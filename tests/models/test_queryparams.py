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


def test_queryparam_rejects_invalid_scalar_types():
    # Plain scalars (int, float, bool) used to leak AttributeError from
    # the internal .items() call, which surfaced as
    # AttributeError: 'int' object has no attribute 'items'. They
    # should now raise TypeError with a clear message naming the
    # supported inputs.
    for value in (42, 3.14, True, False, object()):
        with pytest.raises(TypeError) as exc_info:
            httpx.QueryParams(value)
        assert "QueryParams requires" in str(exc_info.value)


def test_queryparam_rejects_malformed_list_items():
    # A list of bare strings (rather than 2-tuples) used to leak
    # IndexError: string index out of range from item[0]. The
    # constructor should now validate each item and raise a clear
    # TypeError instead.
    with pytest.raises(TypeError) as exc_info:
        httpx.QueryParams(["a", "b"])
    assert "2-tuples" in str(exc_info.value)

    # A 3-tuple is also invalid - same error path.
    with pytest.raises(TypeError):
        httpx.QueryParams([("a", "1", "extra")])


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
