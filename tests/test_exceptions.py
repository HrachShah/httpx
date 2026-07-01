from __future__ import annotations

import typing

import httpcore
import pytest

import httpx

if typing.TYPE_CHECKING:  # pragma: no cover
    from conftest import TestServer


def test_httpcore_all_exceptions_mapped() -> None:
    """
    All exception classes exposed by HTTPCore are properly mapped to an HTTPX-specific
    exception class.
    """
    expected_mapped_httpcore_exceptions = {
        value.__name__
        for _, value in vars(httpcore).items()
        if isinstance(value, type)
        and issubclass(value, Exception)
        and value is not httpcore.ConnectionNotAvailable
    }

    httpx_exceptions = {
        value.__name__
        for _, value in vars(httpx).items()
        if isinstance(value, type) and issubclass(value, Exception)
    }

    unmapped_exceptions = expected_mapped_httpcore_exceptions - httpx_exceptions

    if unmapped_exceptions:  # pragma: no cover
        pytest.fail(f"Unmapped httpcore exceptions: {unmapped_exceptions}")


def test_httpcore_exception_mapping(server: TestServer) -> None:
    """
    HTTPCore exception mapping works as expected.
    """
    # Use 127.0.0.1 on a port that nothing is listening on so the connection
    # is guaranteed to fail.
    # (The previous test used port 123456, which is out of the valid TCP/UDP
    # range and is now rejected at the URL boundary by normalize_port.)
    unreachable = server.url.copy_with(host="127.0.0.1", port=1)
    with pytest.raises(httpx.ConnectError):
        httpx.get(unreachable)

    with pytest.raises(httpx.ReadTimeout):
        httpx.get(
            server.url.copy_with(path="/slow_response"),
            timeout=httpx.Timeout(5, read=0.01),
        )


def test_request_attribute() -> None:
    # Exception without request attribute
    exc = httpx.ReadTimeout("Read operation timed out")
    with pytest.raises(RuntimeError):
        exc.request  # noqa: B018

    # Exception with request attribute
    request = httpx.Request("GET", "https://www.example.com")
    exc = httpx.ReadTimeout("Read operation timed out", request=request)
    assert exc.request == request
