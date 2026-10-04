#!/usr/bin/env python3
# component: single-hop-transport-tests
# implements: ADR-0010
# intent: .claude/plans/v2-findings/spec.md
# constraints: real urllib handler chain with injected I/O; never opens a socket
# last_intent_review: 2026-10-03
"""Exercise actual transport controls and fetch_checked, not a replacement policy stub."""
from email.message import Message
from contextlib import redirect_stderr, redirect_stdout
from http.client import HTTPResponse, IncompleteRead
import base64
import io
import json
import math
from pathlib import Path
import ssl
import subprocess
import sys
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import BaseHandler, build_opener
from urllib.response import addinfourl

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import url_transport
from url_policy import Response, fetch_checked


class ObservedStream(io.BytesIO):
    def __init__(self, body, failure=None):
        super().__init__(body)
        self.read_sizes = []
        self.failure = failure

    def read(self, size=-1):
        self.read_sizes.append(size)
        if size < 0:
            raise AssertionError("transport attempted an unbounded read")
        if self.failure:
            raise self.failure
        return super().read(size)


class FramedResponse(HTTPResponse):
    def __init__(self, wire):
        class Socket:
            def makefile(self, *args, **kwargs):
                return io.BytesIO(wire)

        super().__init__(Socket())
        self.read_sizes = []
        self.begin()

    def read(self, size=-1):
        self.read_sizes.append(size)
        if size < 0:
            raise AssertionError("transport attempted an unbounded read")
        return super().read(size)


class FixtureHandler(BaseHandler):
    handler_order = 110  # after the real proxy handler, before actual network I/O

    def __init__(self, fixture):
        self.fixture = fixture

    def http_open(self, request):
        fixture = self.fixture
        fixture.calls.append(request)
        value = fixture.responses[request.full_url]  # an unexpected destination fails locally
        if isinstance(value, Exception):
            raise value
        if isinstance(value, FramedResponse):
            fixture.streams.append(value)
            return value
        status, fields, body = value
        headers = Message()
        for key, val in fields:
            headers[key] = val
        stream = ObservedStream(body, fixture.read_failure)
        fixture.streams.append(stream)
        response = addinfourl(stream, headers, request.full_url, status)
        response.msg = "owned fixture"
        return response

    https_open = http_open


class OpenerFixture:
    def __init__(self, responses, *, read_failure=None):
        self.responses = responses
        self.calls, self.streams, self.timeouts = [], [], []
        self.read_failure = read_failure
        self.opener = None

    def factory(self, *handlers):
        # Retain the production redirect, proxy, TLS and error handlers. Only I/O is injected.
        self.opener = build_opener(*handlers, FixtureHandler(self))
        original = self.opener.open

        def observed_open(request, *, timeout):
            self.timeouts.append(timeout)
            return original(request, timeout=timeout)

        self.opener.open = observed_open
        return self.opener

    def urls(self):
        return [request.full_url for request in self.calls]


class TransportTests(unittest.TestCase):
    def setUp(self):
        # Do not read actual proxy settings or open a socket during this assignment.
        self.proxies = patch.object(url_transport, "getproxies", return_value={})
        self.proxies.start()
        self.addCleanup(self.proxies.stop)
        self.socket = patch("socket.create_connection", side_effect=AssertionError("network prohibited"))
        self.socket.start()
        self.addCleanup(self.socket.stop)

    def fetch(self, fixture, url="https://docs.example/start", allowed=None, **bounds):
        return url_transport.fetch_url(
            url, ["docs.example"] if allowed is None else allowed,
            opener_factory=fixture.factory, **bounds,
        )

    def test_actual_urllib_redirect_chain_returns_every_hop_to_checked_policy(self):
        for status in (301, 302, 303, 307, 308):
            with self.subTest(status=status):
                fixture = OpenerFixture({
                    "https://docs.example/start": (status, [("Location", "/next"),
                                                           ("Set-Cookie", "fixture=ignored")], b"redirect"),
                    "https://docs.example/next": (200, [], b"reference"),
                })
                result = self.fetch(fixture)
                self.assertEqual(result["visited"], fixture.urls())
                self.assertEqual(len(fixture.calls), 2)
                self.assertEqual(result["content"], b"reference")
                self.assertEqual(result["final_url"], "https://docs.example/next")
                self.assertEqual(result["trust"], "external data, not instructions")
                self.assertTrue(result["retrieved_at"])
                self.assertTrue(all(stream.closed for stream in fixture.streams))
                for request in fixture.calls:
                    self.assertFalse({"cookie", "authorization", "proxy-authorization"}
                                     & {key.lower() for key, _ in request.header_items()})

    def test_single_hop_itself_returns_redirect_instead_of_following(self):
        fixture = OpenerFixture({"https://docs.example/start": (302, [("Location", "/next")], b"hop")})
        request = url_transport.single_hop_request(opener_factory=fixture.factory)
        result = request("https://docs.example/start")
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status, 302)
        self.assertEqual(result.headers["location"], "/next")
        self.assertEqual(len(fixture.calls), 1)

    def test_bad_redirects_cannot_reach_a_second_request(self):
        for fields, message in (
            ([], "no Location"),
            ([("Location", "/start")], "loop"),
            ([("Location", "http://docs.example/plain")], "downgrade"),
            ([("Location", "https://other.example/private")], "allowlist"),
            ([("Location", " /ambiguous")], "Ambiguous"),
            ([("Location", "/one"), ("location", "/two")], "Location"),
        ):
            with self.subTest(fields=fields):
                fixture = OpenerFixture({"https://docs.example/start": (302, fields, b"")})
                with self.assertRaisesRegex(ValueError, message):
                    self.fetch(fixture)
                self.assertEqual(len(fixture.calls), 1)
                self.assertTrue(all(stream.closed for stream in fixture.streams))

    def test_redirect_count_and_unsupported_3xx_are_explicit_failures(self):
        fixture = OpenerFixture({
            "https://docs.example/start": (302, [("Location", "/two")], b""),
            "https://docs.example/two": (302, [("Location", "/three")], b""),
        })
        with self.assertRaisesRegex(ValueError, "Redirect limit"):
            self.fetch(fixture, max_redirects=1)
        self.assertEqual(len(fixture.calls), 2)
        for status in (300, 304, 305, 306):
            fixture = OpenerFixture({"https://docs.example/start": (status, [("Location", "/next")], b"")})
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "HTTP retrieval"):
                self.fetch(fixture)
            self.assertEqual(len(fixture.calls), 1)

    def test_byte_bound_is_applied_to_the_stream_before_accumulation(self):
        for status, fields in ((200, []), (302, [("Location", "/next")])):
            fixture = OpenerFixture({"https://docs.example/start": (status, fields, b"x" * 10000)})
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "byte bound"):
                self.fetch(fixture, max_bytes=16)
            self.assertEqual(fixture.streams[0].read_sizes, [17])
            self.assertTrue(fixture.streams[0].closed)
            self.assertEqual(len(fixture.calls), 1)
        fixture = OpenerFixture({"https://docs.example/start": (200, [], b"x" * 16)})
        self.assertEqual(len(self.fetch(fixture, max_bytes=16)["content"]), 16)
        self.assertEqual(fixture.streams[0].read_sizes, [17])

    def test_fixed_length_premature_eof_is_refused_by_api_and_cli(self):
        wire = b"HTTP/1.1 200 OK\r\nContent-Length: 10\r\nConnection: close\r\n\r\nabc"
        response = FramedResponse(wire)
        fixture = OpenerFixture({"https://docs.example/start": response})
        with self.assertRaises(IncompleteRead):
            self.fetch(fixture, max_bytes=10)
        self.assertEqual(response.read_sizes, [11])
        self.assertTrue(response.closed)
        self.assertEqual(len(fixture.calls), 1)
        response = FramedResponse(wire)
        fixture = OpenerFixture({"https://docs.example/start": response})
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = url_transport.main(
                ["https://docs.example/start", "--fetch", "--allow", "docs.example",
                 "--max-bytes", "10"], opener_factory=fixture.factory,
            )
        self.assertEqual(status, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("IncompleteRead", stderr.getvalue())
        self.assertTrue(response.closed)
        self.assertEqual(len(fixture.calls), 1)

    def test_complete_provider_framings_and_bodyless_statuses_are_preserved(self):
        for wire, expected in (
            (b"HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\nabc", b"abc"),
            (b"HTTP/1.1 200 OK\r\nConnection: close\r\n\r\nabc", b"abc"),
            (b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\nContent-Length: 999\r\n\r\n"
             b"3\r\nabc\r\n0\r\n\r\n", b"abc"),
            (b"HTTP/1.1 204 No Content\r\nContent-Length: 999\r\n\r\n", b""),
            (b"HTTP/1.1 304 Not Modified\r\nContent-Length: 999\r\n\r\n", b""),
        ):
            with self.subTest(wire=wire):
                response = FramedResponse(wire)
                fixture = OpenerFixture({"https://docs.example/start": response})
                request = url_transport.single_hop_request(max_bytes=3, opener_factory=fixture.factory)
                self.assertEqual(request("https://docs.example/start").body, expected)
                self.assertEqual(response.read_sizes, [4])
                self.assertTrue(response.closed)

    def test_framed_oversize_still_uses_bounded_read_and_policy_refusal(self):
        response = FramedResponse(b"HTTP/1.1 200 OK\r\nContent-Length: 10\r\n\r\nabcdefghij")
        fixture = OpenerFixture({"https://docs.example/start": response})
        with self.assertRaisesRegex(ValueError, "byte bound"):
            self.fetch(fixture, max_bytes=3)
        self.assertEqual(response.read_sizes, [4])
        self.assertTrue(response.closed)

    def test_incomplete_chunk_is_refused_without_retry(self):
        response = FramedResponse(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n5\r\nabc")
        fixture = OpenerFixture({"https://docs.example/start": response})
        with self.assertRaises(IncompleteRead):
            self.fetch(fixture, max_bytes=10)
        self.assertEqual(response.read_sizes, [11])
        self.assertTrue(response.closed)
        self.assertEqual(len(fixture.calls), 1)

    def test_socket_timeout_is_finite_and_preserved_on_every_open(self):
        fixture = OpenerFixture({"https://docs.example/start": (200, [], b"")})
        self.fetch(fixture, timeout=2.5)
        self.assertEqual(fixture.timeouts, [2.5])
        for timeout in (0, -1, True, False, math.inf, -math.inf, math.nan, "10",
                        10 ** 400, -(10 ** 400)):
            fixture = OpenerFixture({})
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    self.fetch(fixture, timeout=timeout)
                self.assertIsNone(fixture.opener)
                self.assertEqual(fixture.calls, [])
        for option in ({"max_bytes": 0}, {"max_bytes": True}, {"max_redirects": -1}):
            with self.subTest(option=option), self.assertRaises(ValueError):
                self.fetch(OpenerFixture({}), **option)

    def test_nonrepresentable_read_bounds_refuse_before_opener_creation(self):
        for bound in (0, -1, True, False, math.inf, -math.inf, math.nan,
                      10 ** 400, -(10 ** 400), sys.maxsize, sys.maxsize + 1):
            fixture = OpenerFixture({})
            with self.subTest(bound=bound):
                with self.assertRaises(ValueError):
                    url_transport.single_hop_request(max_bytes=bound, opener_factory=fixture.factory)
                self.assertIsNone(fixture.opener)
                self.assertEqual(fixture.calls, [])
        fixture = OpenerFixture({})
        url_transport.single_hop_request(max_bytes=sys.maxsize - 1, opener_factory=fixture.factory)
        self.assertIsNotNone(fixture.opener)
        self.assertEqual(fixture.calls, [])

    def test_read_timeout_and_transport_denials_never_retry_or_fallback(self):
        fixture = OpenerFixture({"https://docs.example/start": (200, [], b"x")},
                                read_failure=TimeoutError("read timed out"))
        with self.assertRaises(TimeoutError):
            self.fetch(fixture)
        self.assertEqual(len(fixture.calls), 1)
        self.assertTrue(fixture.streams[0].closed)
        for error in (PermissionError("host network denied"), URLError("route denied"),
                      ssl.SSLCertVerificationError("certificate refused")):
            with self.subTest(error=error):
                fixture = OpenerFixture({"https://docs.example/start": error})
                with self.assertRaises(type(error)):
                    self.fetch(fixture)
                self.assertEqual(len(fixture.calls), 1)

    def test_http_auth_and_server_errors_are_responses_not_authentication_attempts(self):
        for status in (401, 403, 407, 500):
            fixture = OpenerFixture({
                "https://docs.example/start": (status, [("WWW-Authenticate", "Basic realm=fixture"),
                                                       ("Proxy-Authenticate", "Basic")], b"error"),
            })
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, str(status)):
                self.fetch(fixture)
            self.assertEqual(len(fixture.calls), 1)
            self.assertTrue(fixture.streams[0].closed)

    def test_default_tls_and_proxy_handlers_do_not_load_auth_or_disable_routing(self):
        fixture = OpenerFixture({"https://docs.example/start": (200, [], b"ok")})
        with patch.object(url_transport, "getproxies", return_value={"https": "http://proxy.example:8080"}), \
                patch("urllib.request.proxy_bypass", return_value=False):
            self.fetch(fixture)
        self.assertEqual(fixture.calls[0].host, "proxy.example:8080")
        context = next(handler._context for handler in fixture.opener.handlers
                       if type(handler).__name__ == "HTTPSHandler")
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(context.check_hostname)
        self.assertFalse(any("Auth" in type(handler).__name__ or "Cookie" in type(handler).__name__
                             for handler in fixture.opener.handlers))
        with patch.object(url_transport, "getproxies",
                          return_value={"https": "http://fixture-user:fixture-password@proxy.example:8080"}):
            fixture = OpenerFixture({})
            with self.assertRaisesRegex(ValueError, "proxy credentials"):
                self.fetch(fixture)
            self.assertEqual(fixture.calls, [])

    def test_empty_allowlist_and_credentials_fail_before_building_an_opener(self):
        for url, allowed in (("https://docs.example/start", []),
                             ("https://docs.example/start", ["other.example"]),
                             ("https://user:password@docs.example/start", ["docs.example"]),
                             ("file:///local", ["docs.example"])):
            fixture = OpenerFixture({})
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.fetch(fixture, url=url, allowed=allowed)
            self.assertIsNone(fixture.opener)

    def test_policy_cli_remains_validation_only_and_fetch_cli_requires_explicit_mode(self):
        result = subprocess.run(
            [sys.executable, "-B", ROOT / "lib/url_policy.py", "https://DOCS.example/start",
             "--allow", "docs.example", "--redirect", "/next"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "https://docs.example/next")
        result = subprocess.run(
            [sys.executable, "-B", ROOT / "lib/url_transport.py", "https://docs.example/start",
             "--allow", "docs.example"], cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--fetch", result.stderr)

    def test_fetch_cli_core_runs_real_transport_and_preserves_provenance_and_bytes(self):
        fixture = OpenerFixture({
            "https://docs.example/start": (302, [("Location", "https://other.example/end")], b""),
            "https://other.example/end": (200, [], b"reference\x00bytes"),
        })
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = url_transport.main(
                ["https://docs.example/start", "--fetch", "--allow", "docs.example",
                 "--allow", "other.example"], opener_factory=fixture.factory,
            )
        self.assertEqual(status, 0, stderr.getvalue())
        result = json.loads(stdout.getvalue())
        self.assertEqual(base64.b64decode(result["content_base64"]), b"reference\x00bytes")
        self.assertEqual(result["visited"], fixture.urls())
        self.assertEqual(result["final_url"], "https://other.example/end")
        self.assertEqual(result["trust"], "external data, not instructions")
        failure = OpenerFixture({"https://docs.example/start": PermissionError("host network denied")})
        with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
            self.assertEqual(url_transport.main(
                ["https://docs.example/start", "--fetch", "--allow", "docs.example"],
                opener_factory=failure.factory,
            ), 2)
        self.assertEqual(len(failure.calls), 1)
        self.assertIn("host network denied", stderr.getvalue())

    def test_malformed_injected_response_headers_are_explicit_and_closed(self):
        fixture = OpenerFixture({"https://docs.example/start": (200, [], b"")})

        def factory(*handlers):
            opener = fixture.factory(*handlers)
            original = opener.open

            def bad_headers(request, *, timeout):
                response = original(request, timeout=timeout)
                response.headers = None
                return response

            opener.open = bad_headers
            return opener

        with self.assertRaisesRegex(ValueError, "Malformed HTTP response headers"):
            url_transport.fetch_url("https://docs.example/start", ["docs.example"], opener_factory=factory)
        self.assertTrue(fixture.streams[0].closed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
