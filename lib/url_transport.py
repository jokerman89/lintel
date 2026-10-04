# component: context-url-transport
# implements: ADR-0010
# intent: .claude/plans/v2-findings/spec.md
# constraints: stdlib single hop; caller needs actual host permission and explicit allowed hosts
# last_intent_review: 2026-10-04
"""Explicit HTTP retrieval, never a workaround for a denied host network operation."""
import argparse
import base64
from contextlib import closing
from http.client import HTTPException, IncompleteRead
import json
import math
import ssl
import sys
from typing import Callable
from urllib.parse import urlsplit
from urllib.request import (
    HTTPErrorProcessor, HTTPSHandler, ProxyHandler, Request, build_opener, getproxies,
)

from url_policy import Response, _response_headers, checked_url, fetch_checked, normalized_url


class _SingleHopResponses(HTTPErrorProcessor):
    """Return every status to policy; urllib must not dispatch redirects/auth retries."""

    def http_response(self, request, response):
        return response

    https_response = http_response


class _NoCredentialProxyHandler(ProxyHandler):
    def __init__(self):
        # Keep ordinary configured routing, including no_proxy. Never fall back to a
        # direct connection or manufacture Proxy-Authorization from a proxy URL.
        proxies = getproxies()
        for scheme in ("http", "https"):
            proxy = proxies.get(scheme)
            if proxy:
                parsed = urlsplit(proxy if "://" in proxy else "http://" + proxy)
                if parsed.username is not None or parsed.password is not None:
                    raise ValueError("Automatic proxy credentials are not supported; use an approved transport.")
        super().__init__(proxies)


def single_hop_request(*, max_bytes: int = 262144, timeout: float = 10.0,
                       opener_factory: Callable = build_opener) -> Callable[[str], Response]:
    """Create one bounded GET callback. The factory seam is for trusted injected I/O.

    An injected factory must retain the supplied handlers, just as build_opener does.
    Host permission is a caller precondition, not something this library can grant.
    The timeout bounds socket operations, not total DNS/redirect-chain wall time.
    Byte limits must leave room for the extra detection byte in a native read size.
    """
    if type(max_bytes) is not int or not 1 <= max_bytes < sys.maxsize:
        raise ValueError("Retrieval byte bound must be a positive integer below the native read-size limit.")
    try:
        valid_timeout = type(timeout) in (int, float) and timeout > 0 and math.isfinite(timeout)
    except OverflowError:
        valid_timeout = False
    if not valid_timeout:
        raise ValueError("Retrieval requires a positive finite timeout.")
    opener = opener_factory(
        _SingleHopResponses(), _NoCredentialProxyHandler(),
        HTTPSHandler(context=ssl.create_default_context()),
    )

    def request(url: str) -> Response:
        selected = normalized_url(url)
        message = Request(selected, headers={"Accept-Encoding": "identity"}, method="GET")
        # A fresh local opener never uses urllib's globally installed opener, cookies,
        # password managers or authentication handlers. Errors propagate, without retry.
        with closing(opener.open(message, timeout=timeout)) as response:
            status = response.getcode()
            if type(status) is not int or not 100 <= status <= 599:
                raise ValueError("Malformed HTTP response status.")
            items = getattr(getattr(response, "headers", None), "items", None)
            if not callable(items):
                raise ValueError("Malformed HTTP response headers.")
            headers = _response_headers(items())
            # read(n) bounds allocation before policy sees the bytes; the extra byte
            # distinguishes an exact fit from an oversized body, even on redirects.
            body = response.read(max_bytes + 1)
            if not isinstance(body, bytes):
                raise ValueError("Transport response body must be bytes.")
            # Bounded HTTPResponse.read permits premature fixed-length EOF.
            # Provider framing already handles chunked and bodyless responses.
            remaining = getattr(response, "length", None)
            if len(body) <= max_bytes and remaining is not None and remaining > 0:
                raise IncompleteRead(body, remaining)
            return Response(status, headers, body)

    return request


def fetch_url(url: str, allowed_hosts: list[str], *, max_redirects: int = 5,
              max_bytes: int = 262144, timeout: float = 10.0,
              opener_factory: Callable = build_opener) -> dict:
    """Wire the real single-hop transport into the existing checked redirect loop.

    Invoke only with actual host network permission and an explicit allowed-host
    decision. Missing capability and an actual denial are different: a denial is
    terminal, never permission to call this helper instead of the refused tool.
    """
    checked_url(url, allowed_hosts)  # reject destination errors before constructing I/O
    return fetch_checked(
        url, allowed_hosts,
        single_hop_request(max_bytes=max_bytes, timeout=timeout, opener_factory=opener_factory),
        max_redirects=max_redirects, max_bytes=max_bytes,
    )


def main(argv=None, *, opener_factory: Callable = build_opener) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--fetch", action="store_true", help="Explicit retrieval; requires actual host permission.")
    parser.add_argument("--allow", action="append", default=[], help="An explicitly authorized host rule.")
    parser.add_argument("--max-redirects", type=int, default=5)
    parser.add_argument("--max-bytes", type=int, default=262144)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args(argv)
    if not args.fetch:
        parser.error("retrieval requires --fetch; use url_policy.py for validation only")
    try:
        result = fetch_url(args.url, args.allow, max_redirects=args.max_redirects,
                           max_bytes=args.max_bytes, timeout=args.timeout, opener_factory=opener_factory)
        # JSON preserves every policy provenance field and the exact bytes without
        # printing arbitrary control characters or claiming a text extraction occurred.
        encoded = {key: value for key, value in result.items() if key != "content"}
        encoded["content_base64"] = base64.b64encode(result["content"]).decode("ascii")
        print(json.dumps(encoded, ensure_ascii=True))
        return 0
    except (ValueError, OSError, HTTPException) as error:
        print(f"url-transport: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
