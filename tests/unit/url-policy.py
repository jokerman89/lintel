# component: url-policy-test
# implements: ADR-0010
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: never opens a socket; actual policy with synthetic HTTP responses
# last_intent_review: 2026-09-20
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from url_policy import Response, checked_url, fetch_checked


class URLPolicyTests(unittest.TestCase):
    def test_exact_and_wildcard_hosts_are_not_interchangeable(self):
        self.assertEqual(checked_url("https://API.Example.com:443/a#part", ["api.example.com"]),
                         "https://api.example.com/a")
        for url in ("https://other.example.com", "https://api.example.com.evil.invalid",
                    "https://sub.api.example.com", "https://example.com"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                checked_url(url, ["api.example.com"])
        self.assertEqual(checked_url("https://a.b.example.com/x", ["*.example.com"]),
                         "https://a.b.example.com/x")
        for url in ("https://example.com", "https://badexample.com"):
            with self.assertRaises(ValueError):
                checked_url(url, ["*.example.com"])

    def test_ambiguous_authority_credentials_and_malformed_policy_fail_closed(self):
        for url in ("file:///tmp/a", "https://api.example.com@evil.invalid",
                    "https://user:password@api.example.com", "https://api.example.com\\@evil.invalid",
                    "https://api.example.com:99999", "https://api.example.com/\nother",
                    "//api.example.com/a", "https://api%2eexample.com", "https://"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                checked_url(url, ["api.example.com"])
        for policy in ([], ["*example.com"], ["https://api.example.com"], ["*.com"], ["*"]):
            with self.subTest(policy=policy), self.assertRaises(ValueError):
                checked_url("https://api.example.com", policy)

    def test_redirect_is_validated_before_transport_observes_target(self):
        calls = []

        def send(url):
            calls.append(url)
            return Response(302, {"Location": "https://other.example.com/private"}, b"")

        with self.assertRaises(ValueError):
            fetch_checked("https://api.example.com/start", ["api.example.com"], send)
        self.assertEqual(calls, ["https://api.example.com/start"])

    def test_relative_and_explicitly_allowed_redirects_succeed_with_provenance(self):
        calls = []
        responses = {
            "https://api.example.com/start": Response(302, {"location": "/next"}, b""),
            "https://api.example.com/next": Response(307, {"Location": "https://docs.example.com/read"}, b""),
            "https://docs.example.com/read": Response(200, {"Content-Type": "text/plain"}, b"documentation"),
        }

        def send(url):
            calls.append(url)
            return responses[url]

        result = fetch_checked("https://api.example.com/start",
                               ["api.example.com", "docs.example.com"], send)
        self.assertEqual(result["content"], b"documentation")
        self.assertEqual(result["visited"], calls)
        self.assertEqual(result["final_url"], "https://docs.example.com/read")

    def test_loops_downgrades_http_errors_and_oversize_are_not_success(self):
        for response in (Response(302, {"location": "/start"}, b""),
                         Response(302, {"location": "http://api.example.com/plain"}, b""),
                         Response(302, {}, b""), Response(500, {}, b"failed"),
                         Response(200, {}, b"x" * 21)):
            calls = []

            def send(url):
                calls.append(url)
                return response

            with self.subTest(response=response), self.assertRaises(ValueError):
                fetch_checked("https://api.example.com/start", ["api.example.com"], send,
                              max_redirects=2, max_bytes=20)
            self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
