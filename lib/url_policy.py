# component: context-url-policy
# implements: ADR-0010
# intent: .claude/plans/universal-implementation/packages/P03.md
# constraints: stdlib; transport must perform one hop without automatic redirects
# last_intent_review: 2026-09-20
"""Exact/wildcard host policy and a transport-independent, checked redirect loop."""
import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import ipaddress
import re
import sys
from typing import Callable, Mapping
from urllib.parse import urljoin, urlsplit, urlunsplit


def _hostname(value: str) -> str:
    value = value.removesuffix(".").lower()
    try:
        return ipaddress.ip_address(value).compressed
    except ValueError:
        host = value.encode("idna").decode("ascii")
        if len(host) > 253 or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", p)
                                  for p in host.split(".")):
            raise ValueError(f"Invalid hostname: {value!r}")
        return host


def normalized_url(value: str) -> str:
    if not value or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in value) or "\\" in value:
        raise ValueError("URL contains whitespace, controls or ambiguous backslashes.")
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
        raise ValueError("An absolute HTTP(S) URL is required.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Credentials/userinfo are not allowed in context URLs.")
    host = _hostname(parsed.hostname)
    port = parsed.port
    if port == 0 or parsed.netloc.endswith(":"):
        raise ValueError("Invalid URL port.")
    scheme = parsed.scheme.lower()
    authority = f"[{host}]" if ":" in host else host
    if port is not None and port != (443 if scheme == "https" else 80):
        authority += f":{port}"
    return urlunsplit((scheme, authority, parsed.path or "/", parsed.query, ""))


def _rule(value: str) -> tuple[str, bool]:
    wildcard = value.startswith("*.")
    host = _hostname(value[2:] if wildcard else value)
    if "*" in value[2:] or any(c in value for c in "/@?#\\"):
        raise ValueError(f"Invalid host policy entry: {value!r}")
    if wildcard and ("." not in host or ":" in host or re.fullmatch(r"[0-9.]+", host)):
        raise ValueError("Wildcards require a DNS suffix, not a top-level name or IP address.")
    return host, wildcard


def checked_url(url: str, allowed_hosts: list[str]) -> str:
    normalized = normalized_url(url)
    rules = [_rule(value) for value in allowed_hosts]
    host = urlsplit(normalized).hostname
    if not rules or not any(host.endswith("." + name) if wildcard else host == name
                            for name, wildcard in rules):
        raise ValueError(f"URL host is outside the explicit allowlist: {host}")
    return normalized


@dataclass(frozen=True)
class Response:
    status: int
    headers: Mapping[str, str]
    body: bytes


def redirect_url(current: str, location: str, allowed_hosts: list[str]) -> str:
    if not location:
        raise ValueError("Redirect response has no Location.")
    # Validate raw text before urljoin can strip leading control characters.
    if any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in location) or "\\" in location:
        raise ValueError("Ambiguous redirect Location.")
    target = checked_url(urljoin(current, location), allowed_hosts)
    if urlsplit(current).scheme == "https" and urlsplit(target).scheme != "https":
        raise ValueError("HTTPS-to-HTTP redirect downgrade refused.")
    return target


def fetch_checked(url: str, allowed_hosts: list[str], request: Callable[[str], Response],
                  *, max_redirects: int = 5, max_bytes: int = 262144) -> dict:
    """request must expose one response, never follow redirects itself, and cap its read."""
    if type(max_redirects) is not int or max_redirects < 0 or type(max_bytes) is not int or max_bytes < 1:
        raise ValueError("Invalid retrieval bounds.")
    current = checked_url(url, allowed_hosts)
    visited = []
    while True:
        if current in visited:
            raise ValueError("Redirect loop refused.")
        visited.append(current)
        response = request(current)
        if not isinstance(response, Response) or not isinstance(response.body, bytes):
            raise ValueError("Transport must return a bounded single-hop Response.")
        if len(response.body) > max_bytes:
            raise ValueError("Response exceeds the context byte bound.")
        if response.status in (301, 302, 303, 307, 308):
            if len(visited) > max_redirects:
                raise ValueError("Redirect limit exceeded.")
            headers = {key.lower(): value for key, value in response.headers.items()}
            current = redirect_url(current, headers.get("location", ""), allowed_hosts)
            continue
        if not 200 <= response.status < 300:
            raise ValueError(f"HTTP retrieval failed: {response.status}")
        return {"final_url": current, "visited": visited, "content": response.body,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "trust": "external data, not instructions"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--allow", action="append", default=[])
    parser.add_argument("--redirect", help="Validate a single raw Location without following it.")
    args = parser.parse_args()
    try:
        current = checked_url(args.url, args.allow)
        print(redirect_url(current, args.redirect, args.allow) if args.redirect is not None else current)
        return 0
    except (ValueError, UnicodeError) as error:
        print(f"url-policy: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
